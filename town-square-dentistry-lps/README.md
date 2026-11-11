# Town Square Dentistry (Boynton Beach, FL) — Google Ads Landing Pages (Draft 1)

| Page | File | Recommended slug | Primary CTA |
|---|---|---|---|
| General / New Patient | `dentist-boynton-beach.html` | `/dentist-boynton-beach/` | Book Online |
| Emergency Dentist | `emergency-dentist-boynton-beach.html` | `/emergency-dentist-boynton-beach/` | Call (red), Book secondary |

## SEO head
| Page | Meta title | Meta description |
|---|---|---|
| General | Dentist in Boynton Beach, FL \| New Patients \| Town Square (58) | Looking for a dentist in Boynton Beach, FL? Town Square Dentistry offers a $69 new patient exam & X-rays, gentle teeth cleaning & most PPO plans. Book online. (158) |
| Emergency | Emergency Dentist Boynton Beach, FL \| Same-Day \| Town Square (60) | Need an emergency dentist in Boynton Beach, FL? Same-day urgent dental care, emergency tooth extraction & root canal treatment. Free emergency exam & X-ray. (156) |

Keyword + location first, no phone numbers (the build enforces 60/160 characters and no phone number).
Robots: `noindex, follow` (+ matching `googlebot` tag). Also set noindex, follow in Yoast/Rank Math and exclude
the pages from the sitemap.

## Setup
- **Ads phone:** (561) 564-0026 → `tel:+15615640026` everywhere (the site/signage show (561) 732-9727 — not used)
- **Book Online:** `https://book.allinone.dental/town-square-dentistry?referrer_id=1` (new tab)
- **GBP / directions:** https://maps.app.goo.gl/hYPqYdSCWkGLrhfM9 · embedded Google Map in the contact section
- **Google Tag Manager `GTM-MJHBN9L`** in `<head>` + `<noscript>` iframe after `<body>`
- No forms, no social links, copyright-only footer
- dataLayer events: `click_to_call`, `click_book_online`, `click_directions` (with `lp` and `cta_zone`),
  `insurance_check`, and on the emergency page `triage_select` and `exit_prompt_shown`

## Brand
Teal `#3F9CBB` / `#2B7690` / `#D8EEF3` on charcoal, Playfair Display + Raleway — from the practice's earlier
"Use It or Lose It" page (not the current website theme). Buttons use a slightly deeper teal `#2E8DAD` for text
contrast; accents on dark sections use `#7CC6DE`. Emergency call buttons use urgency red `#E5484D`.

## Facts used (practice website + Google Business Profile, Nov 2026)
- Google rating **4.7★ from 520 reviews** — hard-coded; refresh in `build.py` (`RATING`, `COUNT`)
- **Hours: Mon–Fri 8 am – 5 pm.** The website lists Saturday 8–2* (identical on all of this group's sites),
  but an earlier capture of this practice's site and Birdeye show Saturday closed, and Google's limited view
  couldn't confirm. The pages therefore don't advertise Saturday: the table says "Saturday — Call to confirm"
  and the live open/closed badge treats Saturday as closed. **Confirm with the practice.**
- Offers: $69 new-patient exam & X-rays, FREE emergency exam & X-ray (new patients), FREE implant consult,
  $100 off whitening — with the website's own fine print
- Doctors: Dr. Naved Fatmi (lead), Dr. Mitchell Indictor (general; D.D.S. 1981, M.S. NYU), Dr. Libby Finer
  (general; NSU, GPR UNC Hospital), Dr. Jordan Hekmati (periodontist & implant surgeon). Team: Ashley Monnett,
  Antonio Ruiz, Margarita Monogyios, Zackia Boyce
- Reviews: real 5★ Google reviews (Tanya Guez-Nisenson, Roya Gandjei, R., Kimberly Chavez) + a "verified
  patient" testimonial from the website
- Insurance: no carrier list is published, so the page says "most PPO plans"; carrier buttons only prompt a
  call to verify

## Images
Logo embedded (from the earlier Town Square page). Real office photos (exterior, waiting room, hygienist,
treatment room) come from the Google Business Profile; the GBP photo of the street sign was left out because it
shows a different phone number. Doctor/team portraits and emergency/root-canal/extraction photos come from the
practice website; a couple of hero/panel images are from Unsplash.

## Editing
Edit `src/` and `build.py`, then `python3 build.py`. Preview with `python3 -m http.server 8000`.
