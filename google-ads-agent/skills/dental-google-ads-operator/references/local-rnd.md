# Local research: the market, the competitors, the offer

Account work stops improving once the account is clean. After that, the wins come
from knowing the local market better than the practice next door does.

## The competitive set

Use `dental-competitor-scraper` for every patient-facing practice within the
radius. What matters per competitor: services, hours (who is open Saturday?),
languages, insurance accepted, new-patient offer, review count and rating, and
whether they advertise.

Then `run_report auction_insights` for who is actually in the auction - the
scraper finds practices, auction insights finds *advertisers*. The gap between
those two lists is useful: a practice with 400 reviews that does not advertise is
a threat to organic bookings, not to your CPC.

Track auction insights month over month. A domain climbing quickly is usually a
practice that just hired an agency; expect CPCs to rise and impression share to
drop before the reports show it as a problem.

## The offer

The new-patient offer is the single biggest lever on conversion rate, and it is
set by the local market, not by best practice. Collect what competitors run:
`$59 exam + x-rays`, `$99 cleaning special`, `free implant consult`,
`$500 off Invisalign`. If the practice's offer is materially worse, no amount of
bid tuning fixes it - say so.

Emergency is different: availability beats price. "Seen today", "open now",
"walk-ins welcome", "we answer 24/7" out-converts a discount.

## Local demand

- `dental-keyword-research-skill` for the keyword set and search volume.
- Seasonality is real in dental: January (new insurance year), late spring
  (pre-summer cosmetic), and December (use-it-or-lose-it benefits) are peaks;
  July-August is soft in most markets. Plan budget around it instead of reacting.
- Insurance mix drives language: in markets dominated by one carrier, naming it in
  the ad lifts CTR noticeably.
- Bilingual markets deserve their own campaign, not translated ad copy inside an
  English one. Spanish-language dental CPCs are usually lower and convert well.

## What to do with it

Research becomes account changes:

- Competitor open Saturday and the practice is not → an operational conversation,
  not a bid change.
- Everyone offering $59 exams and the practice offers nothing → landing page and
  offer work first.
- A new advertiser taking impression share on implants → decide deliberately
  whether to defend on price, on availability, or by moving budget elsewhere.
