# Optimisation rules

Every rule here states the evidence it needs before it fires. That is the whole
point: most damage in a small dental account comes from acting on ten clicks.

A rule that has not met its threshold is not "no finding" - it is "not yet". Say
so, with the number of conversions still needed.

## Keywords

| Decision | Fires when | Why there |
|---|---|---|
| Pause as dead | 0 conversions AND (100+ clicks OR spend ≥ 3× target CPA), 30 days | At 3× target CPA you have paid for three patients and received none. Below ~100 clicks a 3% conversion rate can produce zero by chance. |
| Flag as expensive | CPA > 2× target with ≥ 1 conversion and spend ≥ 2× target | Not dead - usually a match-type or landing-page problem, not a bid problem. |
| Tighten match type | Broad keyword whose search terms are mostly off-intent | Broad belongs in a dental account only with a strong negative list and smart bidding. |
| Low Quality Score | QS ≤ 4 with 25+ clicks | Fix the ad-to-keyword-to-page match. Bidding more into a 4 is buying your way out of a copy problem. |

Never pause a keyword that produced a conversion in the last 30 days without
saying so explicitly.

## Bidding (target CPA)

- **Minimum evidence: 30 conversions in the trailing 30 days.** Below that, report
  the CPA and do nothing.
- **Maximum step: 10-15% per week.** Smart bidding re-learns after a change; a 40%
  move throws away two weeks of learning to save a week of impatience.
- **Lower** when CPA > 1.3× target with enough conversions.
- **Raise** when CPA ≤ target AND search impression share lost to rank > 20% - that
  is demand you are already earning and can afford.
- **Never touch** in a campaign's first 14 days, or within a week of the last change.
- **No target set** on Maximize Conversions means "spend the budget at any cost". Set
  one from the practice's patient value, not from the current CPA.

Starting target CPA for a new campaign = average patient value × acceptable
acquisition share. Practical starting points, until the account has its own data:
emergency 8-12% of first-visit value, general 10-15% of first-year value, implants
5-8% of case value.

## Budget

- Raise **only** when search impression share lost to budget > 10% **and** CPA ≤
  target **and** there are ≥ 10 conversions. Two of three is not enough.
- Step: +20%, then wait a week.
- Budget-limited **and** over target is not a budget problem. Say that plainly:
  more budget buys more expensive clicks.
- Under 70% budget use is not a budget problem either - look at impression share,
  bids, and whether the keyword set is too small.

## Ads and assets

- Replace assets Google labels LOW after 1,000+ impressions. Keep at least 8
  headlines and 3 descriptions live.
- Pin sparingly. One pinned position 1 headline for the offer or "Emergency
  Dentist Open Now" is fine; pinning everything turns an RSA into an expanded
  text ad and Ad Strength drops.
- Ad Strength POOR or AVERAGE is worth fixing, but Ad Strength is not a
  performance metric - never pause a converting ad because of it.
- Disapproved ad = zero delivery. Same-day fix, always.

## Schedule

- Compare spend by hour with the practice's front-desk hours.
- If more than 15% of spend lands when nobody answers and there is no answering
  service: bid those hours down 30-50%, or route the calls. Do not simply switch
  hours off in emergency campaigns - toothache is a 2am business.
- Require two consecutive weeks showing the same pattern before changing hour
  modifiers. One week of hour-level data is mostly noise.

## Geography

- Exclude a postal code after ≥ 25 clicks and spend ≥ 2× target CPA with zero
  bookings - and check drive time before you do, because a ZIP can be close on a
  map and awkward to reach.
- Bid up a postal code booking at ≤ 0.7× target CPA.
- Rebuild the demographic plan monthly; let actual bookings override the model
  wherever there is enough data (`gads.zips.reconcile_with_performance`).

## Calls

- Qualified call = 60 seconds or longer, unless the practice says otherwise.
- Under 40% qualified is a traffic problem or a front-desk problem, not a bidding
  problem. Listen to five calls before changing the account.
- Missed calls are the cheapest fix in the account. Report them every time.

## What "enough data" means

| Decision | Minimum |
|---|---|
| Pause a keyword | 100 clicks or 3× target CPA spent |
| Move target CPA | 30 conversions / 30 days |
| Move budget | 10 conversions and lost IS (budget) > 10% |
| Postal-code exclusion | 25 clicks and 2× target CPA |
| Hour-of-day modifier | 2 consecutive weeks, 40+ clicks in the slot |
| Ad copy verdict | 1,000 impressions per asset |
