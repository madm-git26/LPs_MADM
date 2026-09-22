# In Smyle Dental — Lakeview &amp; Roscoe Village — "Use It or Lose It" Landing Page

A fresh, conversion-focused Google Ads landing page for **In Smyle Dental** (Dr. Jose M. Mariscal, DDS),
replacing the practice's old 2023 "claim insurance benefits" page for the year-end dental-insurance
campaign. Built for Display / Performance Max traffic, aimed at one goal: **book before the 2026
benefits deadline.**

| Page | File | Notes |
|---|---|---|
| Use It or Lose It | `use-it-or-lose-it.html` | Production source — links to `assets/`, deploy this with the folder alongside it |
| Use It or Lose It (standalone) | `InSmyle-Dental-Lakeview-Use-It-Or-Lose-It.html` | Everything bundled into one file — download and double-click to preview, no server needed. Regenerate with `python3 bundle.py use-it-or-lose-it.html InSmyle-Dental-Lakeview-Use-It-Or-Lose-It.html` after editing the source |

Phone number used on this page: **(773) 915-6530** (`tel:+17739156530`) — the tracking number supplied
for this campaign; the main site itself lists (773) 915-6270.
Book online link: **https://book.allinone.dental/in-smyle-dental?referrer_id=6**

## Brand colors — kept exactly as used on insmyledental.com

Per your instruction, colors were **not invented or adjusted** — they're pulled directly from the live
site's own CSS:

| Token | Hex | Where it's used on the real site |
|---|---|---|
| Orange (primary/CTA) | `#F87132` | Button backgrounds site-wide, including the physical office signage |
| Teal (secondary) | `#006882` | Section backgrounds, link/hover color |
| Slate (body text) | `#576166` | Body copy |

The real logo (light cyan-blue + red "In Smyle... is always In Style") is used as-is, unaltered.

## Setup before running traffic

1. **Conversion tracking** — paste your Google tag in the `<head>`, fill in `ADS_CONVERSION_ID`,
   `LABEL_CALL`, `LABEL_BOOK` in `assets/js/lp.js`. Same event model as other projects in this repo:
   `click_to_call`, `click_book_online`, `click_directions`.
2. **Countdown deadline** — set once in `assets/js/lp.js` (`DEADLINE_ISO`), currently
   `2026-12-31T23:59:59-06:00` (America/Chicago). Bump the year for future campaigns.
3. Remove `<meta name="robots" content="noindex, nofollow">` only if you want this indexed.

## Sourced from

- **Existing page** (`book.insmyledental.com/claim-insurance-benefits/`): kept the "benefits don't roll
  over" explainer and the December-rush stat, rebuilt everything else.
- **Main site** (`insmyledental.com`): real brand colors (above), Dr. Mariscal's real bio and
  credentials (UIC College of Dentistry with honors, Fellow of the Academy of General Dentistry — top
  7% nationally), real office hours, accepted insurance carriers (with their real logos), the "Best of
  2026" award badge, and real office photography.
- **Reviews**: 4.9★ aggregate and three real, attributed reviews (Robert S., Brittany M., Jorge D.),
  sourced from the practice's public Google review aggregation.
