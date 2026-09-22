# Regency Court Dentistry — Boca Raton, FL — "Use It or Lose It" Landing Page

A fresh, conversion-focused Google Ads landing page for **Regency Court Dentistry** (Dr. Naved Fatmi,
DMD), for the year-end dental-insurance campaign. Built for Display / Performance Max traffic, aimed at
one goal: **book before the 2026 benefits deadline.**

| Page | File | Notes |
|---|---|---|
| Use It or Lose It | `use-it-or-lose-it.html` | Production source — links to `assets/`, deploy this with the folder alongside it |
| Use It or Lose It (standalone) | `Regency-Court-Dentistry-Boca-Raton-Use-It-Or-Lose-It.html` | Everything bundled into one file — download and double-click to preview, no server needed. Regenerate with `python3 bundle.py use-it-or-lose-it.html Regency-Court-Dentistry-Boca-Raton-Use-It-Or-Lose-It.html` after editing the source |

Phone number used on this page: **(561) 979-2003** (`tel:+15619792003`) — the tracking number supplied
for this campaign; the main site itself lists (561) 998-0727.
Book online link: **https://book.allinone.dental/regency-court-dental?referrer_id=3**

## Brand colors — pulled from the live site, not invented

Sourced by directly curling and grepping the real site's own CSS (`dg-colors.css`, the child theme
stylesheet), not a paraphrased summary:

| Token | Hex | Where it's used on the real site |
|---|---|---|
| Green (primary/CTA) | `#9AC444` | Button backgrounds (`.btn-tertiary`), active nav states, link/icon accents — confirmed 17+ times in the site's own stylesheet |
| Charcoal (structural) | `#242424` / `#292929` / `#3F3F3F` | Dark nav/section backgrounds, secondary buttons |

Fonts are the same two the site loads: **Playfair Display** (headings) and **Raleway** (body).

## Setup before running traffic

1. **Conversion tracking** — paste your Google tag in the `<head>`, fill in `ADS_CONVERSION_ID`,
   `LABEL_CALL`, `LABEL_BOOK` in `assets/js/lp.js`. Same event model as the other projects in this repo:
   `click_to_call`, `click_book_online`, `click_directions`.
2. **Countdown deadline** — set once in `assets/js/lp.js` (`DEADLINE_ISO`), currently
   `2026-12-31T23:59:59-05:00` (America/New_York, EST by year-end). Bump the year for future campaigns.
3. Remove `<meta name="robots" content="noindex, nofollow">` only if you want this indexed.

## What's on the page

Same trimmed ~5-fold structure as the other two projects: sticky urgency top bar → header → hero with
live countdown + a real patient photo, "USE IT OR LOSE IT" led → trust strip → one merged **USE IT OR
LOSE IT** section (quick stat row, 100/80/50% coverage tiers, payment/insurance options, a "before you
book" list, and a benefit checklist with one CTA) → a short doctor bio card (single photo, two
credential chips) → 4.6★ reviews (animated counters) → location/hours/map → final CTA with a second
countdown → a copyright-only footer (no link columns) → sticky mobile call/book bar. No services grid,
no step-by-step process section, no gallery.

## Sourced from — and a note on what's *not* claimed

- **"Previous" landing page** (`book.dentistrybocaratonfl.com/dentist-boca-raton/`): checked first —
  turns out it isn't actually a "use it or lose it" page at all. It's a generic, poorly-maintained
  evergreen offer page with real bugs (an opening headline left over from an unrelated New Jersey
  market template, two of three testimonials naming a different doctor — "Dr. Despointes" — than the
  one profiled, and a stray Arizona-area-code phone number on one CTA). Nothing from it carried over
  except the confirmed real facts (address, Dr. Fatmi's bio, the general PPO-insurance framing).
- **Main site** (`regencycourtdentistry.com`): real brand colors and fonts (above), office hours, and
  Dr. Fatmi's real, verified bio — DMD from the University of Florida College of Dentistry, founded the
  practice in 2012, appointed to the Florida Board of Dentistry in 2015 (its youngest-ever member),
  later Vice Chair and Chairman. Real photos (his headshot, a patient photo) pulled from the site's own
  CloudFront asset bucket.
- **Reviews**: 4.6★ aggregate (site's own schema.org rating) and three real, attributed reviews (Gary
  K., Elena Fontanazza, Nicholas G.), independently sourced via web search against the practice's public
  review listings.
- **Insurance carriers**: the site's own accepted-insurance list is populated by JavaScript, not present
  in the static HTML, so no specific carrier names could be verified — this page deliberately says
  "most PPO plans" rather than naming carriers it can't confirm. The 100/80/50% coverage breakdown is
  presented as a typical PPO structure, not a claim specific to this practice's own plan.
- The practice's real "Lifetime Dental Care" program is mentioned as a genuine differentiator.

## Files

```
use-it-or-lose-it.html                                                production source
Regency-Court-Dentistry-Boca-Raton-Use-It-Or-Lose-It.html              bundled, downloadable single file
bundle.py                                                              regenerates the standalone bundle
assets/css/theme.css       brand tokens + all components (green/charcoal palette)
assets/js/lp.js            countdown, scroll-reveal, animated counters, hours logic, tracking
assets/img/                real practice photography + logo
```

### Preview locally

```bash
python3 -m http.server 8000
# then open http://localhost:8000/use-it-or-lose-it.html
```
