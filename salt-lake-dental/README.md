# Salt Lake Dental — Teeth Cleaning Landing Page (Google Ads)

A conversion-focused Google Ads landing page for **Salt Lake Dental**
(2120 S 700 E STE I, Salt Lake City, UT 84106), built to match the live site at
https://www.saltlakedental.net/ — same palette (pine/sage green, brand rust, cream),
serif display + Poppins typography, and the practice's real photos, doctors, hours
and review quotes. Nothing on the page is invented.

| Page | File |
|---|---|
| Teeth Cleaning / Preventive | `teeth-cleaning.html` |

Phone number used everywhere: **(801) 396-9321** (`tel:+18013969321`).
Booking CTA everywhere: the practice's own Modento scheduler —
`https://book.modento.io/salt-lake-dental` (opens in a new tab).

## Before you run traffic

1. **Google Ads conversion tracking** — paste your Google tag (gtag.js) snippet into
   the `<head>`, then fill in the constants at the top of the inline script at the
   bottom of the page:

   ```js
   var ADS = {
     ID: 'AW-XXXXXXXXX',   // your conversion ID
     LABEL_CALL: '...',    // click-to-call conversion label
     LABEL_BOOK: '...'     // book-online conversion label
   };
   ```

   Events already fire (to `gtag`, `dataLayer` and `fbq` when present):

   | Event | Trigger |
   |---|---|
   | `click_to_call` | any `tel:` link — header, hero, location, final CTA, sticky mobile bar |
   | `click_book_online` | any Modento booking link |
   | `click_directions` | the Google Maps / reviews links |

2. **`noindex`** — the page ships with `<meta name="robots" content="noindex, nofollow">`
   so it never competes with saltlakedental.net organically. Google Ads serves it fine
   either way.

## Page structure

Hero (keyword-matched H1 + call/book CTAs + live open/closed status + 4.6★ rating) →
trust bar (Google rating, Saturdays, PPO, free parking) → 5-step "what's included"
visit walkthrough → preventive services grid → why-us (transparent pricing, Saturday
hours, fast new-patient scheduling, modern office) → Dr. Tysen Carter + Brooke (RDH) →
verbatim patient reviews → insurance/financing → location, hours table (today
highlighted) + embedded map → 6-question FAQ → final CTA → sticky mobile call/book bar.

Everything is a single self-contained HTML file (inline CSS/JS, local images,
Google Fonts only) for fast loads and easy hosting anywhere.
