# Lake Worth Dentistry (Greenacres, FL) — Google Ads Landing Pages (Draft 1)

| Page | File | Recommended slug | Primary CTA |
|---|---|---|---|
| General / New Patient | `dentist-lake-worth.html` | `/dentist-lake-worth/` | Book Online |
| Emergency Dentist | `emergency-dentist-lake-worth.html` | `/emergency-dentist-lake-worth/` | Call (red), Book secondary |

## SEO head
| Page | Meta title | Meta description |
|---|---|---|
| General | Lake Worth Dentist in Greenacres, FL \| New Patients Welcome (59) | Looking for a dentist in Lake Worth or Greenacres, FL? $69 new patient exam & X-rays, gentle cleanings, Saturday hours & most PPO plans. Book online today. (151) |
| Emergency | Emergency Dentist Lake Worth & Greenacres FL \| Same-Day Care (60) | Need an emergency dentist in Lake Worth or Greenacres, FL? Same-day urgent dental care, emergency tooth extraction & chipped tooth repair. Free emergency exam. (157) |

Keyword + location first, no phone numbers (the build fails if one is added or a title/description goes over
60/160 characters). Robots: `noindex, follow` (+ matching `googlebot` tag). In WordPress also set the page to
noindex, follow in Yoast/Rank Math and exclude it from the sitemap.

## Setup
- **Ads phone:** (561) 771-6540 → `tel:+15617716540` everywhere (the website lists (561) 649-6446 — not used)
- **Book Online:** `https://book.allinone.dental/lake-worth-dentistry?referrer_id=3` (new tab)
- **GBP / directions:** https://maps.app.goo.gl/Pm2TNk8EZXfFy3HU8 · embedded Google Map in the contact section
- **Google Tag Manager `GTM-5J22NPZS`** in `<head>` + `<noscript>` iframe after `<body>`
- No forms, no social links, copyright-only footer
- dataLayer events: `click_to_call`, `click_book_online`, `click_directions` (with `lp` and `cta_zone`),
  `insurance_check`, and on the emergency page `triage_select` and `exit_prompt_shown`

## Brand
Purple `#775FA0` / `#5F4880` / `#EFEAF6` on charcoal, Playfair Display + Raleway — from the practice's earlier
"Use It or Lose It" page (not the current website theme). A lighter purple `#C3B3E0` is used for accents on
dark sections for contrast. Emergency call buttons use urgency red `#E5484D`.

## Facts used (practice website + Google Business Profile, Nov 2026)
- Google rating **4.7★ from 459 reviews** — hard-coded; refresh in `build.py` (`RATING`, `COUNT`)
- Hours Mon–Fri 8–5, Sat 8–2, Sun closed; live open/closed status in America/New_York
- Offers: $69 new-patient exam & X-rays, FREE emergency exam & X-ray (new patients), FREE implant consult,
  $100 off whitening — with the website's own fine print
- Doctors: Dr. Naved Fatmi (lead), Dr. Mauricio Antezana (general & cosmetic), Dr. Jordan Hekmati
  (periodontist & implant surgeon). Team: Antonio Ruiz, Leyvis Vazquez (no photo on site — initial avatar),
  Dakiya Nixon, Bella Isma
- Reviews: real 5★ Google reviews (Rosalie Fernandez, Duncan McKinley, Steven Curtiss, Marie Armand) + a
  "verified patient" testimonial from the website
- Insurance: no carrier list is published, so the page says "most PPO plans"; carrier buttons only prompt a
  call to verify

## Images
Logo is the practice's purple logo, embedded (it has no public URL). Real office photos (treatment room,
interior, front desk) come from the Google Business Profile; doctor/team portraits and service photos from the
practice website; hero backdrops partly from Unsplash. One GBP photo showing a storefront signed
"Florida Family Dental" was deliberately left out.

## Editing
Edit `src/` and `build.py`, then `python3 build.py`. Preview with `python3 -m http.server 8000`.
