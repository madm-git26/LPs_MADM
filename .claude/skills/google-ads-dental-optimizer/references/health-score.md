# ACCOUNT HEALTH SCORE (0–100)

The score is a summary of the diagnosis, never a substitute for it. Report it as
`ACCOUNT HEALTH: XX/100`, then explain the sub-scores that cost the most points, in order.

Compute it with `scripts/health_score.py` so the same account state always produces the same
number and every point can be defended input by input:

```bash
python3 scripts/health_score.py --example > metrics.json   # template to fill in
python3 scripts/health_score.py metrics.json
python3 scripts/health_score.py --self-test                # verify the rules
```

## Weights

Tracking is weighted highest because every other dimension is measured through it — a tracking
fault makes the rest of the score meaningless. Lead quality outranks cost efficiency because a
cheap unqualified lead is worth nothing to a dental practice.

| Dimension | Weight | Key |
|---|---:|---|
| Tracking health | 20 | `tracking` |
| Lead quality | 15 | `lead_quality` |
| Cost efficiency | 15 | `cost_efficiency` |
| Search quality | 12 | `search_quality` |
| Traffic health | 10 | `traffic` |
| Location quality | 8 | `location` |
| Campaign structure | 8 | `structure` |
| Landing page / conversion | 7 | `conversion` |
| Budget & bidding | 5 | `budget_bidding` |
| **Total** | **100** | |

## Missing data

Every input is optional. An absent or `null` input is **unscored**, never assumed:

- A dimension is scored on whichever of its sub-inputs are present, renormalised over them.
- A dimension with no inputs at all is excluded, and the total is renormalised over the rest.
- The output always states its own coverage, e.g. *"Scored on 72% of the rubric by weight"*, and
  lists the unscored dimensions under `DATA NOT AVAILABLE — CANNOT CONFIRM`.

Never fill a gap with a plausible number to make the score look complete. A 78/100 at 60% coverage
is an honest result; a 78/100 built from three guesses is a fabrication.

## Bands

| Score | Band | Meaning |
|---|---|---|
| 85–100 | HEALTHY | Optimize at the margin; protect what works |
| 70–84 | STABLE — fixable gaps | Clear opportunities, no emergency |
| 50–69 | AT RISK | Structural problems consuming real budget |
| 30–49 | POOR | Multiple layers broken; sequence the fixes |
| 0–29 | CRITICAL | Stop scaling; likely a tracking or targeting fault |

## Inputs and thresholds

`lin(v, a, b)` scores 0 at `a` and 1 at `b`, linear between, clamped outside. When `a > b`, lower
is better.

### Tracking health (20)

| Input | Weight | Rule |
|---|---:|---|
| `has_primary_conversion` | .30 | true → 1, false → 0 |
| `crm_variance_pct` | .20 | ≤10% → 1 · ≤25% → 0.7 · ≤50% → 0.35 · else 0 (absolute value) |
| `days_with_zero_conversions_last_30` | .15 | 0 → 1 · ≤2 → 0.6 · ≤6 → 0.3 · else 0 |
| `duplicate_conversion_actions` | .15 | 0 → 1 · 1 → 0.5 · else 0 |
| `auto_tagging_enabled` | .10 | boolean |
| `call_conversion_threshold_seconds` | .10 | ≥60 → 1 · ≥30 → 0.6 · else 0.2 |

`crm_variance_pct` = `(google_conversions − crm_leads) / crm_leads × 100`. Score it in both
directions: over-reporting misleads bidding, under-reporting starves a working account.

### Lead quality (15)

| Input | Weight | Rule |
|---|---:|---|
| `qualified_lead_rate_pct` | .40 | `lin(v, 30, 70)` |
| `booked_rate_pct` | .40 | `lin(v, 20, 60)` |
| `spam_rate_pct` | .20 | `lin(v, 25, 0)` |

Requires call review or CRM data. If unavailable, leave the whole dimension out and say so — do
not substitute Google's conversion count, which is the thing this dimension exists to check.

### Cost efficiency (15)

| Input | Weight | Rule |
|---|---:|---|
| `cost_per_qualified_lead_ratio` | .70 | `lin(v, 2.0, 0.8)` — actual ÷ target |
| `cpa_trend_pct` | .30 | `lin(v, 50, 0)` — 30d vs prior 30d |

Cost per **qualified** lead, not CPA. If lead qualification is unavailable, note that the ratio is
computed on raw conversions and is therefore an upper bound on true efficiency.

### Search quality (12)

| Input | Weight | Rule |
|---|---:|---|
| `high_intent_spend_pct` | .50 | `lin(v, 30, 70)` |
| `wasted_spend_pct` | .35 | `lin(v, 15, 0)` |
| `negative_list_present` | .15 | boolean |

Both percentages come from classifying search terms against `search-term-taxonomy.md`. State the
share of spend the search-terms report actually covers — Google withholds low-volume terms.

### Traffic health (10)

| Input | Weight | Rule |
|---|---:|---|
| `search_impression_share_pct` | .40 | `lin(v, 20, 65)` |
| `lost_is_budget_pct` | .20 | `lin(v, 30, 0)` |
| `lost_is_rank_pct` | .20 | `lin(v, 60, 15)` |
| `clicks_trend_pct` | .20 | `lin(v, -30, 0)` |

Impression-share metrics come back as fractions 0–1; multiply by 100 before entering them here.

### Location quality (8)

| Input | Weight | Rule |
|---|---:|---|
| `in_area_spend_pct` | .50 | `lin(v, 60, 95)` |
| `presence_only_targeting` | .30 | boolean |
| `top_zip_spend_concentration_pct` | .20 | `lin(v, 50, 25)` |

`in_area_spend_pct` = share of spend on `LOCATION_OF_PRESENCE` inside the service area (§6.1).

### Campaign structure (8)

| Input | Weight | Rule |
|---|---:|---|
| `services_segmented` | .30 | boolean — emergency / implants / ortho / general split |
| `brand_separated` | .25 | boolean |
| `single_keyword_spend_share_pct` | .25 | `lin(v, 50, 20)` |
| `pmax_search_cannibalization` | .20 | true → 0, false → 1 |

### Landing page / conversion (7)

| Input | Weight | Rule |
|---|---:|---|
| `conversion_rate_ratio` | .50 | `lin(v, 0.25, 1.25)` — actual ÷ target |
| `mobile_desktop_cvr_ratio` | .30 | `lin(v, 0.3, 0.9)` |
| `dedicated_landing_pages` | .20 | boolean — not the site homepage |

### Budget & bidding (5)

| Input | Weight | Rule |
|---|---:|---|
| `budget_limited_campaigns_with_good_cpa` | .40 | 0 → 1 · 1 → 0.6 · 2 → 0.3 · else 0 |
| `strategy_appropriate` | .40 | boolean |
| `underspend_pct` | .20 | `lin(v, 40, 10)` |

`budget_limited_campaigns_with_good_cpa` counts campaigns losing impression share to budget
**while** hitting CPA target — capped upside, which is a loss, not a saving.

## Reporting the score

Always give the score, the coverage, and the top three point losses with the inputs that caused
them. A score without its drivers is a vanity metric, which is exactly what this agent does not
produce.
