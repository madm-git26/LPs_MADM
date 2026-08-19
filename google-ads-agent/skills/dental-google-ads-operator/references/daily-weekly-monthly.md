# What to check, and when

The cadence matters as much as the checks. A daily bid change is a bad habit; a
monthly negative sweep is money already spent.

## Daily (10 minutes) - `run_routine daily`

1. **Spend anomalies.** Yesterday vs the trailing daily average, per campaign.
   ±40% is worth a look; zero spend on a live campaign is an emergency.
2. **Disapprovals.** A disapproved ad delivers nothing. Fix today.
3. **New search terms** from the last 7 days - block obvious waste.
4. **Call quality.** How many calls ran 60s+, how many were missed.
5. **Anything from yesterday's changes** - the audit log tells you what the agent
   itself did.

Daily proposes negatives only. Bids, budgets and pausing wait for the weekly run,
where there is enough data to be right.

## Weekly (45 minutes) - `run_routine weekly`

1. **Search term mining** over 30 days: negatives, plus terms worth promoting to
   keywords.
2. **Dead keyword sweep** against the thresholds.
3. **Target CPA review** - one step, only where the evidence supports it.
4. **Budget review** - raise only where efficiency is already there.
5. **Schedule** and **postal-code** performance.
6. **Ads and assets** - replace LOW assets, check ad strength, verify each ad group
   still has at least one enabled ad.
7. **Impression share**: where is the loss - rank or budget? They have opposite
   fixes.

## Monthly (2 hours) - `run_routine monthly`

1. **Conversion tracking audit.** Are the primary actions still the ones that mean
   a patient? Did someone add a "page view" conversion?
2. **Auction insights** vs last month. A domain climbing fast usually means a new
   competitor or a new agency next door - expect CPCs to follow.
3. **Structure review.** Are ad groups still tight? Has one campaign quietly become
   80% of spend?
4. **Rebuild the ZIP/income plan** and reconcile it with real postal-code results.
5. **Landing pages and the offer.** Conversion rate by page, and whether the new
   patient offer still matches what competitors are running.
6. **The practice conversation**: patients booked, patients seen, revenue per
   patient - against ad spend. That is the only scoreboard that matters.

## Quarterly

- Re-run keyword research (`dental-keyword-research-skill`) and the local
  competitive set (`dental-competitor-scraper`).
- Re-derive target CPAs from updated patient value, not last quarter's targets.
- Review the negative list for terms that have quietly blocked real patients.
