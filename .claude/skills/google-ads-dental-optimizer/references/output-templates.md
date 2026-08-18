# OUTPUT TEMPLATES

Every deliverable opens with one connection-status line:

```
CONNECTION: <tool name> · customer <ID> · <account name> · <currency> · <time zone> · read-only|read-write
```

or, when there is none:

```
CONNECTION: NONE — DATA NOT AVAILABLE, CANNOT CONFIRM
```

---

## Recommendation block

The unit of output. Never abbreviate it, never merge fields.

```
[P0] Emergency campaign is paying for out-of-area clicks

PROBLEM
  38% of Emergency campaign spend went to users outside the 10-mile service area.

EVIDENCE
  geographic_view, Jul 19 – Aug 17: $1,847 of $4,860 campaign spend on
  location_type = AREA_OF_INTEREST. Those clicks produced 3 conversions vs 41 from
  LOCATION_OF_PRESENCE. Campaign geo setting is PRESENCE_OR_INTEREST.  [CONFIRMED]

ROOT CAUSE
  Positive geo target type is set to PRESENCE_OR_INTEREST, so the campaign serves to
  people merely researching the area, not located in it.

ACTION
  Set campaign.geo_target_type_setting.positive_geo_target_type = PRESENCE on the
  Emergency campaign.

EXPECTED IMPACT
  Recovers roughly $1,800/month of spend into in-area traffic. At the in-area
  conversion rate this is ~14 additional qualified leads/month at current CPC.
  [HIGH PROBABILITY — assumes in-area conversion rate holds as volume shifts]

RISK
  Slight volume reduction in the first 7–10 days while the campaign re-learns.
  Travellers legitimately searching for an emergency dentist while visiting the area
  will no longer be reached — historically 3 conversions in 30 days.

ROLLBACK
  Revert the single setting to PRESENCE_OR_INTEREST. Immediate, no data loss.

CONFIDENCE  High
PRIORITY    P0
```

Priorities: **P0** money burning now or tracking broken · **P1** material efficiency loss ·
**P2** meaningful upside, not urgent · **P3** hygiene and long-term structure.

---

## Daily run

```
CONNECTION: ...
DATE: <account timezone date> · comparing <window> vs <prior window>

ANOMALIES
  🔴 ...   (metric, delta, absolute values, affected entity)
  🟠 ...
  🟡 ...
  none → "No anomalies above threshold."

WHAT MOVED
  Spend / clicks / conversions / CPA vs prior period, with the inflection date if any.

NEW FINDINGS
  Search terms, keywords, locations worth acting on. Evidence inline.

ACTIONS TAKEN (safe, auto-applied)
  - <action> — <reason> — rollback: <how>
  none → "None."

AWAITING APPROVAL
  <recommendation blocks, P0 first>
  none → "None."

DATA NOT AVAILABLE
  <what could not be retrieved and why>
```

---

## Weekly report

```
CONNECTION: ...
PERIOD: <dates> vs <prior dates>

EXECUTIVE SUMMARY
  3–5 sentences. What happened, why, what it costs, what to do. No metric dumps.

ACCOUNT HEALTH: XX/100  (<band>, scored on XX% of the rubric)
  Top point losses and their drivers.

TOP PROBLEMS
  Ranked, each with severity and dollar impact.

TOP WINNING CAMPAIGNS        TOP LOSING CAMPAIGNS
  spend · conv · CPA · trend   spend · conv · CPA · trend

TOP WINNING KEYWORDS
  keyword · match · spend · conv · CPA · classification

WASTED SPEND
  $X (Y% of total). Itemised by cause: out-of-area, wrong service, informational,
  jobs/education, non-converting keywords. Each line ties to an action below.

SEARCH TERM FINDINGS
  Intent mix vs prior period. New negatives proposed. New keywords worth adding.
  Coverage: the % of spend the search-terms report accounts for.

LOCATION FINDINGS
  Best and worst ZIPs/cities by cost per qualified lead. Distance-band read.

CONVERSION QUALITY
  Google conversions vs qualified leads vs booked appointments.
  Cost per qualified lead. Cost per booked appointment.
  Tracking reliability verdict.

ROOT CAUSES
  Which of the 6 levels is broken, and the evidence chain. Explicitly say when the
  answer is level 6 and Google Ads is not the primary problem.

RECOMMENDED ACTIONS
  Full recommendation blocks, ranked.

TEST PLAN
  What to test, the hypothesis, the metric that decides it, the duration, and the
  minimum data needed for the result to mean anything.

NEXT 7 DAYS PRIORITIES
  1. 2. 3. — each with an owner (agent / client) and a check date.
```

---

## Audit closing block

Every audit ends with exactly this, and nothing after it:

```
MAIN PROBLEM
  One sentence.

ROOT CAUSE
  One sentence.

TOP 3 ACTIONS
  1.
  2.
  3.

EXPECTED RESULT
  What should improve, by roughly how much, and by when.

RISK
  What could go wrong, and the early warning sign to watch.

DATA NEEDED
  What additional information would sharpen the diagnosis, and who can supply it.
```

---

## Writing rules

- Lead with the finding, not the table. Tables support a claim; they are not the claim.
- Every number carries its date range. A number without a window is unverifiable.
- Every diagnostic sentence carries `CONFIRMED` / `HIGH PROBABILITY` / `POSSIBLE` / `UNKNOWN`.
- Express impact in qualified leads, booked appointments, and dollars — not in CTR points.
- When something could not be retrieved, say `DATA NOT AVAILABLE — CANNOT CONFIRM` and name the
  query or resource that failed. Silence about a gap reads as a claim there is no gap.
