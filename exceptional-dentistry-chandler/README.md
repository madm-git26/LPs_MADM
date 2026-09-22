# Exceptional Dentistry of Chandler — "Use It or Lose It" Landing Page

A fresh, conversion-focused Google Ads landing page for **Exceptional Dentistry of Chandler**
(Dr. Eric W. Hwang, DDS), replacing the practice's old 2024 "claim insurance benefits" page for the
year-end dental-insurance campaign. Built for Display / Performance Max traffic, aimed at one goal:
**book before the 2026 benefits deadline.**

| Page | File | Notes |
|---|---|---|
| Use It or Lose It | `use-it-or-lose-it.html` | Production source — links to `assets/`, deploy this with the folder alongside it |
| Use It or Lose It (standalone) | `Exceptional-Dentistry-Chandler-Use-It-Or-Lose-It.html` | Everything (CSS, JS, images) bundled into one file — download and double-click to preview, no server or folder needed. Regenerate after editing the source with `python3 bundle.py use-it-or-lose-it.html Exceptional-Dentistry-Chandler-Use-It-Or-Lose-It.html` |

Phone number used on this page: **(480) 806-2601** (`tel:+14808062601`) — a tracking number supplied
for this campaign; the main site itself lists (480) 806-2602.
Book online link: **https://book.allinone.dental/exceptional-dentistry**

---

## Before you run traffic — required setup

### 1. Google Ads conversion tracking

Paste your Google tag in the `<head>` of `use-it-or-lose-it.html`, then fill in the labels in
`assets/js/lp.js`:

```js
ADS_CONVERSION_ID: 'AW-XXXXXXXXX',
LABEL_CALL: '...',   // click-to-call conversion label
LABEL_BOOK: '...',   // book-online click conversion label
```

Events already fire on every interaction (to `gtag`, `fbq` and `dataLayer`):

| Event | Trigger |
|---|---|
| `click_to_call` | any `tel:` link — topbar, header, hero, final CTA, mobile bar |
| `click_book_online` | any link to `book.allinone.dental` — header, hero, insurance section, final CTA, mobile bar |
| `click_directions` | the Google Maps / directions links |

There is no lead form on this page — the two conversion paths are **Call** and the practice's own
**Book Online** scheduler (AllInOne Dental), per the brief. Every "Book" CTA opens it in a new tab.

### 2. Update the countdown deadline every year

The live countdown (hero, top bar, final CTA) counts down to a date set once in `assets/js/lp.js`:

```js
DEADLINE_ISO: '2026-12-31T23:59:59-07:00'   // Arizona (Phoenix) does not observe DST, so this offset is fixed year-round
```

Bump the year on this line — and in the footer copyright and page copy mentioning "2026" — before
reusing this page for a future benefit year.

### 3. Remove `noindex` if you want this page indexed

It ships with `<meta name="robots" content="noindex, nofollow">` so it doesn't compete with the main
site in organic search. Google Ads serves it fine either way.

---

## Research this page is based on

- **Existing page** (`book.smilearizona.net/claim-insurance-benefits/`): dated, image-broken 2024
  page — kept the two things that were actually working (the "benefits don't roll over" explainer and
  a real stat about December patients being unable to get seen), rebuilt everything else.
- **Main website** (`smilearizona.net`): sourced the real brand palette (burgundy `#6C0018`, gold and
  lavender from the practice's own logo), heading font (Cormorant Garamond), Dr. Hwang's real bio,
  credentials, office hours, accepted insurance, and real photography (doctor headshot, family photo,
  patient-experience and before/after images — all pulled from the practice's own site and re-optimized
  as WebP for this page).
- **Reviews**: 5.0★ aggregate and three real, attributed patient reviews (Zachary Glover, Tim Batzer,
  Dominique Ramirez), sourced from the practice's public Google review aggregation. Refresh the rating
  summary and review cards periodically from the practice's live Google Business Profile.
- **Competitor / industry research**: current "use it or lose it" dental landing pages (Avalon Dental,
  Nexus Dental, Bel Drive Dental, and others) and 2026 dental-PPC CRO benchmarks — countdown urgency,
  clear coverage-tier breakdowns, testimonials, and dual call/book CTAs are the patterns that
  consistently convert for this exact campaign type, which is why this page leads with all four.

## What's on the page

Trimmed to ~5 folds on desktop (~4,200px) per feedback on the first draft. Sticky urgency top bar →
header (logo, call, book) → hero with live countdown + real patient photo, "USE IT OR LOSE IT" led →
trust strip → one merged **USE IT OR LOSE IT** section (quick stat row on the deadline, the 100/80/50%
coverage tiers, accepted PPO plans, a "before you book" list and a patient-benefit checklist, all in one
place so insurance is explained clearly without being spread across separate sections) → a short Dr.
Hwang bio card (single photo, two credential chips) → 5.0★ reviews (animated counters) →
location/hours/map → final CTA with a second countdown → a copyright-only footer (no link columns) →
sticky mobile call/book bar.

Cut from the original draft on request: the services grid, the "how it works" step section, and the
before/after gallery — all in service of keeping the page short and CTA-focused.

All scroll animations (`data-reveal`) and the animated stat counters both fail open: if JavaScript never
runs, nothing is hidden; if it does run, a 3.5-second fallback timer finishes the job for anything the
scroll observer hasn't caught yet (including the "5.0" / "350+" counters), so nothing is ever stuck at
a placeholder value — verified against a full-page, no-scroll capture.

## Files

```
use-it-or-lose-it.html                                  the landing page (production source)
Exceptional-Dentistry-Chandler-Use-It-Or-Lose-It.html    same page, bundled into one downloadable file
bundle.py                                                regenerates the standalone bundle from the source
assets/css/theme.css       brand tokens + all components (burgundy/gold/lavender palette)
assets/js/lp.js            countdown, scroll-reveal, animated counters, hours logic, tracking
assets/img/                real practice photography + logo, optimized to WebP/PNG
```

### Preview locally

```bash
python3 -m http.server 8000
# then open http://localhost:8000/use-it-or-lose-it.html
```

Use a server rather than opening the file directly — the Google Maps embed needs `http://`.
