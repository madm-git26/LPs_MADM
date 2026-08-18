# ROOT-CAUSE PLAYBOOK

Work the six levels **in order**. Each level's integrity is a precondition for the next: a tracking
fault makes every conversion-rate conclusion below it meaningless, and a traffic collapse makes
cost analysis a distraction. Name the broken layer explicitly before recommending anything.

---

## Level 1 — TRACKING

*If this level is broken, stop. Fix tracking before optimizing anything. Smart bidding trained on
bad conversion data will actively destroy the account.*

Run `gaql-library.md` §1.4, §3.1, §3.2.

Check, in order:

| Check | Fault signature | Severity |
|---|---|---|
| Any conversion action `primary_for_goal = true`? | None primary → `metrics.conversions` is 0 while `all_conversions` is not; smart bidding has no target | 🔴 |
| Sudden drop to zero for one action | Tag removed, site redeploy, consent-mode change, GTM container overwritten | 🔴 |
| Two actions counting the same event | e.g. a "Call" action **and** a "Phone Click" action on the same tel: link | 🟠 |
| `counting_type = MANY_PER_CLICK` on a lead action | One patient clicking call 4 times = 4 conversions; inflates volume, misleads bidding | 🟠 |
| `phone_call_duration_seconds` threshold | Set below ~60s, every wrong number counts as a lead | 🟠 |
| `always_use_default_value = true` on all actions | Every lead worth the same → value-based bidding is meaningless | 🟡 |
| Lookback window unusually long | 90-day click-through on emergency dental over-credits ads | 🟡 |
| `customer.auto_tagging_enabled = false` | Breaks GCLID, breaks offline conversion import | 🟠 |
| Imported/offline conversions present? | Absent → the account cannot see booked-vs-inquired at all | 🟠 |

**The inflation test.** When CRM or practice-management data is available, compare:

```
Google Ads reported conversions (30d)  vs  actual leads in the CRM (30d)
```

A gap beyond roughly 25% is a tracking-reliability finding, not a performance finding. Example:
100 Google conversions against 35 real leads means the account is optimizing toward a number that
does not exist. Report it as 🔴 and do not recommend aggressive bidding changes until resolved.

Also test the reverse: fewer Google conversions than CRM leads means under-tracking — real
performance is better than reported, and the account may be under-invested.

**Never optimize aggressively until tracking reliability is established.**

---

## Level 2 — TRAFFIC

Run §2.1, §2.2.

- Impressions down + impression share flat → **market demand fell** (seasonality, local event,
  search interest). Not an account fault. Check YoY for the same weeks before concluding.
- Impressions down + impression share down → **you lost eligibility**: budget, bid, Quality Score,
  ad disapproval, or a targeting change. Go to §Level 3 and change history.
- Impressions flat + clicks down → **CTR fell**: ad rotation, a new/disapproved ad, competitor
  offer, or a lost ad-position tier. Check §7.1 approval status first — it is the cheapest fix.
- Impressions **up** while conversions are flat → often a match-type or targeting loosening pulled
  in weaker traffic. Go to Level 4.

Dental seasonality worth knowing before calling a decline a problem: benefits-driven surges in
Nov–Dec (use-it-or-lose-it), a January reset (new deductibles suppress elective work), summer
pediatric peaks around school physicals, and general softness over major holiday weeks. Compare
YoY, not just MoM, before diagnosing a "decline."

---

## Level 3 — COST

Run §2.1, §11.

- Avg CPC up >20% with impression share flat → **auction pressure**. Verify the same budget now
  buys fewer clicks. Not fixable by bidding alone; needs Quality Score or offer work.
- Avg CPC up with impression share **up** → the bidding strategy is buying more aggressively,
  usually after a tCPA/tROAS change or a switch to Maximize Conversions. Check change history.
- `search_budget_lost_impression_share > 0.10` → budget-constrained. Quantify the ceiling:
  `available impressions ≈ current impressions / search_impression_share`.
- `search_rank_lost_impression_share` high → bid or Quality Score, not budget. Adding budget here
  wastes money; it will not buy the impressions.
- Spend up while conversions flat/down → find where the incremental spend went (§4, §5, §6.1).
  It is almost always concentrated: one keyword, one term, one geo, one device.

---

## Level 4 — SEARCH QUALITY

Run §4, §5, §5.1.

Classify every search term against `search-term-taxonomy.md`. Then compute the traffic mix:

```
% of spend on HIGH INTENT terms  (target: >60% for a mature dental Search account)
% of spend on IRRELEVANT + JOB + EDUCATIONAL  (target: <5%)
```

A mix that has shifted between periods is a direct, quantified cause of a CPA rise, and one you
can act on immediately.

Common structural causes of a bad mix:
- Broad match added or match type loosened without a negative list to match
- Smart Bidding + broad match with weak conversion signal (Level 1 fault upstream)
- A new campaign with no negative list inheriting the account's junk
- Display Expansion / search partners enabled on a Search campaign (§1.3)
- Missing brand negatives in non-brand campaigns → brand traffic inflating apparent performance

---

## Level 5 — CONVERSION

Run §7.3, §8, then examine the landing page directly if web access is available.

- Conv. rate down while traffic mix is unchanged (Level 4 clean) → the **page or the offer**
  changed, or something broke. Load the page. Check the phone link, the booking widget, the form,
  and mobile rendering.
- Mobile conv. rate collapsing while desktop holds → a mobile-specific break. Most common: a
  `tel:` link that stopped firing the conversion, or a booking iframe that fails on mobile.
- Conv. rate down on one landing page only → isolate and compare against the others.
- Calls stable but call **duration** collapsing (§3.3) → the calls are being generated but not
  handled. That is Level 6.
- New offer from a competitor can move conv. rate with nothing changed on your side. Supporting
  context only; never the first hypothesis.

---

## Level 6 — BUSINESS

This is where dental accounts most often actually break, and where reports most often stop too
early.

Check, when the data is reachable:

- Qualified calls vs total calls
- Missed / abandoned calls, especially during open hours
- Average speed to answer, and after-hours handling
- Booking rate on answered qualified calls
- Appointment availability — an account cannot book into a schedule that is full for 5 weeks
- Follow-up on unbooked inquiries
- Whether new-patient slots are being blocked by hygiene recall

**The definitive test:**

```
Clicks stable → Calls stable → Bookings down
```

That pattern is not a Google Ads problem. State it in the required words:

> "The available evidence indicates that Google Ads is not the primary problem. The main issue
> appears to be occurring after the lead is generated."

Then quantify what it costs. If 40 qualified calls produced 12 bookings where they used to produce
24, the recoverable value of fixing call handling exceeds anything available from bid tuning, and
the recommendation should say so in dollars.

---

## Keyword classification thresholds

Minimum evidence before any classification: **30 days** of data, and the click thresholds below.
Below threshold the answer is TEST, never PAUSE.

| Class | Criteria | Action |
|---|---|---|
| **SCALE** | ≥3 conversions in 30d, CPA ≤ target, qualified-lead rate healthy, impression share <80% | Raise budget/bid ceiling; check lost IS for headroom |
| **KEEP** | Converting at or near target, no headroom or already dominant | Leave alone; monitor |
| **TEST** | <30 clicks in 30d, or <2 conversions — insufficient data | Give it time or controlled budget; do **not** judge yet |
| **REDUCE** | ≥30 clicks, CPA 1.5–3× target, some conversions | Lower bid, tighten match type, add negatives — before pausing |
| **PAUSE** | ≥50 clicks and 0 conversions in 60d, **or** CPA >3× target across 60d with no quality-lead evidence | Pause — only after checking history, seasonality, and lead quality |
| **NEGATIVE** | Intent is wrong, not performance | Add as negative at the right level |

Before executing any PAUSE, run the §2.2 daily trend for that keyword's ad group and confirm the
poor performance is not a recent, recoverable dip inside a strong 12-month history.

**Never** pause a keyword on 1–2 days of data. **Never** pause a keyword whose CPA rose this week
but which produced qualified patients consistently for months.

---

## Anomaly severity

Compare the trailing 7 days against the prior 28-day baseline, unless noted.

| Signal | 🔴 CRITICAL | 🟠 HIGH | 🟡 MEDIUM | 🟢 LOW |
|---|---|---|---|---|
| Conversions | zero for 2+ days on a spending campaign | −40% | −20% | −10% |
| Spend with flat conversions | +50% | +30% | +15% | +10% |
| CPA | +75% | +40% | +20% | +10% |
| Avg CPC | +50% | +30% | +15% | +10% |
| CTR | −40% | −25% | −15% | −10% |
| Conv. rate | −40% | −25% | −15% | −10% |
| Calls | zero during open hours | −40% | −20% | −10% |
| Single keyword's share of campaign spend | >50% with CPA above target | >35% | >25% | — |
| Single ZIP/city share of campaign spend | >40% with below-average conv. rate | >30% | >20% | — |
| Conversion volume doubling overnight | 2× with no spend change → suspect tracking | +50% | — | — |
| Impression share lost to budget | >30% | >20% | >10% | — |

Two rules on top of the table:

1. **A sudden doubling of conversions is a 🔴 tracking alert, not a win**, until proven otherwise
   in Level 1. Celebrating a duplicate tag is the most expensive mistake in this playbook.
2. Small accounts produce large percentages from small absolute numbers. Require a **minimum
   absolute change** — at least 5 conversions or $250 of spend — before escalating past 🟡.
