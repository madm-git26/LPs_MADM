# Lake Worth Dentistry — Greenacres, FL — "Use It or Lose It" Landing Page

⚠️ **Not yet ready to run traffic.** This page is complete except for one deliberately-unfilled piece:
the reviews section (`#reviews`) currently shows a `0.0` / `0+` placeholder instead of a real rating.

## Why it's blocked

Research turned up a real discrepancy that needed the client's input before publishing a number:

- The practice's own site self-reports two different, inconsistent ratings in its own schema.org
  markup: 5.0★/268 reviews in one block, 4.7★/421 in another.
- The only independently-verifiable third-party source found (Yelp, via the exact URL the practice's
  own site links to as its official Yelp page) showed **1.5★ from 6 reviews**, with several substantive
  negative reviews (billing complaints, a patient describing being referred to the Boca Raton office
  mid-root-canal, professionalism complaints).
- Only one clearly positive, attributable review could be verified for this specific location:
  **Sthefany A.** (5★, "I had the best experience going to this dentist!...", truncated on the source
  page).

Rather than guess or publish an unsubstantiated star-rating claim on a paid ad page, this was flagged to
the client, who is checking their live Google Business Profile for the real current number.

## To finish this page

1. Get the real rating and review count from the client.
2. Fill in `#reviews` in `use-it-or-lose-it.html`: replace the `data-count-to="0"` placeholders on the
   score and review-count spans, and the "Rated on Google" line, with the real values.
3. If the client also confirms the site's own review count (268 vs 421) or the Yelp figure is the more
   accurate one, add `aggregateRating` back into the JSON-LD `<script>` block in `<head>` (it was
   intentionally omitted rather than publish a placeholder or unverified number in structured data).
4. Optionally reinstate a `hero-badge.badge-rating` in the hero (CSS already supports it, see
   `.hero-badge.badge-rating` in `assets/css/theme.css`) once a real number exists.
5. Re-render and screenshot-check, then generate the standalone bundle:
   `python3 bundle.py use-it-or-lose-it.html Lake-Worth-Dentistry-Use-It-Or-Lose-It.html`
   (copy `bundle.py` from one of the other projects in this repo first — not yet added here).

## Everything else is real and ready

- **Brand colors**: purple `#775FA0` (site's own `btn-tertiary`/CTA color) + charcoal, pulled directly
  from the live site's `dg-colors.css`, not invented.
- **Doctor**: Dr. Naved Fatmi, DMD — same real, verified bio as the Regency Court Dentistry project
  (Florida Board of Dentistry Chairman). Note: research found it's ambiguous whether Fatmi personally
  treats patients at this specific Greenacres location day-to-day, or whether it's primarily run by
  associate dentists (Dr. Mauricio Antezana is also listed for this location) — the page follows the
  practice's own public-facing framing (Fatmi as the featured doctor) per the task brief, without
  claiming his daily on-site presence.
- **Financing**: CareCredit®, LendingClub and Sunbit — all real, confirmed via direct links on the
  practice's own Patient Information page.
- **Insurance carriers**: not named specifically — the site doesn't list named PPO carriers anywhere in
  its static content, so the page says "most PPO plans" rather than naming carriers that couldn't be
  verified.
- **"Previous" landing page** (`book.dentistgreenacresfl.com/claim-insurance-benefits/`): unlike the
  Regency Court project, this one genuinely is real "use it or lose it" content (correct address,
  correct doctor name) — but carries real template-leftover bugs that were NOT reused: a meta
  description for an unrelated practice ("Expressions Dental Care – Dr. John Han"), a stray Texas-area-
  code phone number buried in one CTA, a testimonial naming a different dentist ("Dr. Ortiz"), and a
  stale year (2025).

Phone number used on this page: **(561) 771-6540** (`tel:+15617716540`).
Book online link: **https://book.allinone.dental/lake-worth-dentistry?referrer_id=3**

## Files

```
use-it-or-lose-it.html     the landing page (production source) — reviews section pending
assets/css/theme.css       brand tokens + all components (purple/charcoal palette)
assets/js/lp.js            countdown, scroll-reveal, animated counters, hours logic, tracking
assets/img/                real practice photography + logo
```
