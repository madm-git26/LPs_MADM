# Joyful Smiles Pediatric Dentistry — Tinley Park, IL — "Use It or Lose It" Landing Page

The first **pediatric** practice in this series. Same structure and standing rules as the previous
seven pages (no services section, no treatment steps, no footer links, short doctor section, clear
insurance section, "USE IT OR LOSE IT" up front, under 5–6 folds), with copy rewritten for
parents booking for their kids.

There was no previous "Use It or Lose It" landing page for this client, so there was no old page
to audit.

## ⚠️ Fix before running ads: the booking page has no form

The Request Appointment link you provided — **https://www.kidsdds.net/book-now/** — is used on every
booking button as instructed. But that page is broken right now: where the form should be, it
literally prints **"Gravity Forms not active"** (the form plugin is switched off in WordPress), so
there is nothing to fill in. Every paid click on "Request Appointment" currently lands on a page with
no way to book. Either reactivate Gravity Forms on kidsdds.net, or send a working booking URL and I'll
swap it in. Until then the amber **Call** buttons are the only working conversion path.

## Rating & reviews — real Google numbers this time

For the first time in this series, the live Google figure was read directly: **4.9★ from 910 Google
reviews** (checked 5 Oct 2026). Two sources agree exactly: Google's own Maps data for this listing,
and the review widget on the practice's own /reviews page (Trustindex, which pulls from the same
Google listing and shows 1-star reviews too, so it isn't filtered).

Other numbers you may see, and why they aren't used:
- **4.8★ / 747** — hard-coded in the practice's own site schema. An old snapshot; Google has moved on.
- **Birdeye 4.8★ / 1,082** — its Google count is 125 higher than Google's own. Not used.
- **Yelp ~3.5★ / 17–18 reviews** — the one real outlier (10 five-star, 6 one-star). Worth knowing,
  not a reason to change the Google figure.

The page shows **4.9★ / 910+** with a date stamp, plus three verbatim parent reviews from Google
(Saif Jaber, Katherine Faulkner, Katie Reed — all 5★, all 2026). `assets/js/gmb-widget.js` is wired
in as on the other pages: add a Places API key and the rating, count and review cards update live on
every page load. See the Lake Worth or Town Square README for key setup steps and the cost note.

## Real facts used on this page

- **Brand colors**, all from the site's own CSS (and the purple confirmed in the logo's pixels):
  purple `#5C2976` (the real "Book now" button), amber `#FFB001` (the real "Call" button — the page
  keeps the same purple-book / amber-call pairing), blue `#0071BC` (the real top bar), dark navy
  `#1D1C3E`, and the site's own playful accents (lime `#B4FF5E`, cyan `#00C6FF`, orange `#FF601C`)
  used for small touches like the coverage-card tops and bullet dots.
- **Fonts**: Signika (everything) and Bad Script (the handwritten accents), both loaded from Google
  Fonts exactly as the real site does.
- **Illustrations**: the elephant, bird and bunny are the practice's own artwork from its site, shown
  as small decorations on desktop and hidden on phones.
- **Doctor**: Dr. Yaa McDonald, DMD, MDS — owner since 2017. DMD from Southern Illinois University;
  pediatric dentistry residency, specialty certificate and Master of Dental Science from the
  University of Tennessee Health Science Center. Her federal NPI record confirms she's a pediatric
  dentistry specialist. Her site bio also says she's a Diplomate of the American Board of Pediatric
  Dentistry — the board's own lookup couldn't be reached to confirm it, so the page doesn't claim
  "board-certified." Add it if the practice confirms.
- **Insurance**: Aetna, Blue Cross Blue Shield, Cigna, Delta Dental, MetLife and United Healthcare —
  each has its own page on the site. The site says in three places that it does **not** accept HMO,
  Medicaid, Public Aid or All Kids plans, and this page says so plainly (important for a pediatric
  practice — many parents assume All Kids is accepted).
- **Financing**: CareCredit only.
- **Hours**: Monday–Friday 9am–5pm, Saturday/Sunday closed — what the site shows and what Google
  shows. **Time zone is Central**, unlike every earlier project: the countdown ends at 11:59 pm CST
  on Dec 31, and the "open now" status uses Chicago time.
- **Address**: 7020 Centennial Drive, Tinley Park, IL 60477.
- **GMB link**: https://goo.gl/maps/unrUpS3G7a9mV47T9 — resolves to "Joyful Smiles Pediatric
  Dentistry Of Tinley Park" and matches the practice's own Google Maps link. Used on the Read Reviews
  button and both Get Directions links; the embedded map searches by business name + address so its
  pin shows the practice, not a bare street address.

## Things on the practice's own site worth flagging to the client

- **Phone numbers**: this page uses the number you gave, **(708) 794-9526**. The live site shows
  (708) 633-8700 everywhere visitors can see it; Google's listing shows (708) 634-5178; and
  794-9526 appears in the site's schema data and on Yelp/WebMD. They're probably call-tracking lines,
  but worth confirming that 794-9526 rings the front desk.
- **Copy from another practice**: hidden homepage text (still read by Google) describes "the
  children's dental office of Joshua Paynich, DDS, PA" — a pediatric dentist in Asheville, NC — and
  the book-now page embeds a Google Map centered on Asheville. Leftovers from a website template. None
  of it is used here.
- **Dr. Sara Day** is labeled "Pediatric Dentist" on part of the site, but her bio and NPI record show
  a general dentist (general dentistry residency). She isn't featured on this page.
- **DMO plans**: the Insurance page says "select DMO plans" are accepted; the Financial Policy page
  says they aren't. This page doesn't mention DMO either way.

## Files

```
use-it-or-lose-it.html                                         the landing page (production source)
Joyful-Smiles-Pediatric-Dentistry-Tinley-Park-Use-It-Or-Lose-It.html   standalone downloadable bundle
assets/css/theme.css                                           brand tokens + all components
assets/js/lp.js                                                countdown (Central time), reveal, hours, tracking
assets/js/gmb-widget.js                                        live Google rating/reviews upgrade — optional
assets/img/                                                    hero photo, doctor photo, logo, illustrations
bundle.py                                                      regenerates the standalone bundle after any edit
```

Phone: **(708) 794-9526** (`tel:+17087949526`) · Request Appointment: **https://www.kidsdds.net/book-now/**


---

# Invisalign® for Kids & Teens — Tinley Park landing page (Google Ads)

`invisalign.html` (+ standalone `Joyful-Smiles-Pediatric-Dentistry-Tinley-Park-Invisalign.html`).
Uses the same Tinley Park theme as the page above — `theme.css` plus `assets/css/invisalign.css` for
the Invisalign-only components — so the purple/amber/blue/navy palette, Signika + Bad Script fonts,
logo, elephant/bird/bunny artwork, reviews, phone **(708) 794-9526**, GMB link and the booking link
**https://www.kidsdds.net/book-now/** all match kidsdds.net. Dr. Elnagar's photo
(`assets/img/doctor-elnagar.jpg`) is the one on his kidsdds.net bio page, cropped inside its frame.

**Booking page update (checked 6 Oct 2026):** kidsdds.net/book-now/ now has a working Typeform embed,
so the "Gravity Forms not active" problem flagged above appears fixed (a leftover Gravity Forms
block still prints that message lower on the page — worth removing).

Insurance wording is Tinley Park's: Aetna, Blue Cross Blue Shield, Cigna, Delta Dental, MetLife and
United Healthcare; not HMO, Medicaid, Public Aid or All Kids. Financing: CareCredit.

**Offer, as briefed:** regular price **$8,000** shown struck through, offer price **$6,500** directly
below it. The $1,500 difference is presented as four "bonus rewards" (layout modeled on the reference
image's dark reward cards with gold corner brackets and value pills — design only, no content taken):

| Reward | Value |
|---|---|
| 01 · Free Retainers | $750 |
| 02 · Free 3D Scan & Smile Preview | $250 |
| 03 · Free Consultation | $150 |
| 04 · Free X-Rays & Records | $350 |
| **Total** | **$1,500** |

Below the cards: "Total Invisalign® Bonus: $1,500 in free rewards — included with every Invisalign®
booking", then a $8,000 − $1,500 = $6,500 strip. The split is my proposal — change the values in the
reward cards, the pricing list and the FAQ if the practice wants different numbers (they must still
add up to $1,500). Each reward was chosen because the practice's own content supports it: the
orthodontic page offers a complimentary consultation, the Invisalign guide on the blog describes the
digital 3D scan with a preview of the future smile, and the practice takes digital X-rays.

**Sections:** hero with the price card → trust strip → $1,500 rewards band → why Invisalign for kids
+ "could it help my child?" checklist → Dr. Mo Elnagar (orthodontist) with Dr. Yaa McDonald →
pricing & ways to pay → Google reviews → FAQ → location & hours → final CTA → footer with offer
terms. No countdown (lp.js skips it when there are no countdown elements), no footer links.

**Where the content comes from:** the practice's own "Invisalign First-Time Patient Guide" blog
post (aligners worn 1–2 weeks each, 20–22 hours a day, 12–18 months typical / as little as six
months, mild pressure for a day or two, Invisalign Teen's compliance indicators and replacement
aligners), the orthodontic-treatment page (early treatment, expanders, space maintainers) and
Dr. Mo Elnagar's bio on the site. His NPI record (1285124792) confirms he's an orthodontics
specialist at UIC's College of Dentistry address.

### Please confirm with the practice before running ads

- **Invisalign provider status.** Neither site has an Invisalign service page; the blog post and
  Dr. Elnagar's bio ("clear aligners") are the only references. The page uses the Invisalign® name
  throughout, so the practice should be an active Invisalign provider (Align's trademark rules).
- **"Board-certified."** Dr. Elnagar's bio says he is board-certified; the ABO directory couldn't be
  checked, so the page doesn't say it (same rule as Dr. McDonald's board claim). Add it if confirmed.
- **Which office/days Dr. Elnagar sees Invisalign patients** — his bio is on both sites.
- **Offer terms in the footer** ("no cash value", "candidacy determined at consultation", etc.) are
  standard wording I added; adjust to whatever the practice wants.

Regenerate the bundle after edits:
`python3 bundle.py invisalign.html Joyful-Smiles-Pediatric-Dentistry-Tinley-Park-Invisalign.html`
