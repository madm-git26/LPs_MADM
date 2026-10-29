# Belmont Dentistry Scottsdale — Google Ads Landing Pages (redesign)

New designs for the two existing landing pages. **Scottsdale office only:** 8350 E Raintree Dr, Suite 115, Scottsdale, AZ 85260.

| Page | File | Replaces |
|---|---|---|
| New Patient / General Dentist | `new-patients-scottsdale.html` | belmontdentistry.com/lp/new-patients-scottsdale/ |
| Emergency Dentist | `emergency-dentist-scottsdale.html` | belmontdentistry.com/lp/emergency-dentist-scottsdale/ |
| Thank-you page (shared by both) | `thank-you-scottsdale.html` | New. Send patients here after they book. |
| Single-file copies | `standalone/*.html` | CSS, JS and every image are built into the file. Use these if you're pasting into a page builder. |

Upload the page and its `assets/` folder together (fastest). For the standalone files, also upload the 6 small files
in `assets/video/` and set `VIDEO_BASE_STANDALONE` in `build.py` to their URL, then rebuild. Until you do, the hero
shows the clinic's photo instead of the video. Nothing breaks.

## Thank-you page

`thank-you-scottsdale.html` is one shared confirmation page for both landing pages. It has:

- an animated gold check and a "Thank You! We'll See You Soon." headline
- three next steps: watch for your confirmation, fill out your forms online, and arrive 10 minutes early
- a "what to bring" list
- a box for rescheduling or pain before the appointment, with a call button
- the three dentists, the comfort menu, and the map, hours and directions

It has no booking buttons. It is `noindex, nofollow` and also loads GTM-PKC6XXJ.

**Conversion tracking.** Before GTM loads, the page pushes `thank_you_view` to `dataLayer`, along with `lp_source`. The
value is `emergency`, `new-patients` or `direct`. It comes from `?from=` in the URL, or from the referring page.

**Setup:**

1. Publish the page, e.g. at `belmontdentistry.com/lp/thank-you-scottsdale/`.
2. In All-in-One Dental, set the Scottsdale booking widget's after-booking redirect to that URL.
3. In GTM, create a Custom Event trigger on `thank_you_view` and fire your Google Ads booking conversion on it.

To split conversions by page, add `?from=emergency` or `?from=new-patients` to the redirect.

## Links & numbers used on every button

- **Phone:** (480) 602-8050 (`tel:+14806028050`). That's 21 call links on the new-patient page and 40 on the emergency page.
- **Book Online:** https://book.allinone.dental/belmont-scottsdale?referrer_id=4. Opens in a new tab.
- **Google Business Profile:** https://maps.app.goo.gl/AYHuqmcoSysNogFbA. Used for the rating badges, "Read all reviews" and Get Directions.
- **Map:** the same Belmont Dentistry Scottsdale Google Maps embed the main site uses.
- **No forms. No social media links. No footer links.**

The main website shows (480) 609-0050 and (480) 605-1380 for Scottsdale. These pages use only the (480) 602-8050 number you supplied.

## What's on each page

**Both pages:** sticky header with call and book buttons, plus a sticky Call / Book bar at the bottom on phones. The
hero runs the Scottsdale office's own film as the background. It loads only after the page itself, plays only while
on screen, has a pause button and respects reduced-motion settings.

The hero shows a Google rating badge (4.9★ · 699 reviews) and a trust-stats bar. Both pages also include:

- the main site's ticker strip
- real Google reviews in a carousel
- doctor cards for Dr. Puneet Sandhu, Dr. Ambreen Sandhu and Dr. Erin Hong
- awards and affiliations: Spear Faculty Club, Invisalign, ADA, AzDA, CADSF and the International Dental Implant Association
- an insurance section: PPO, the Belmont Dental Plan, CareCredit and accepted payment methods
- an office photo tour
- an FAQ
- a map with the address, the rating again, hours, a live open/closed status and directions
- a final CTA

**Every section ends with a CTA.**

**New patient page:**
1. Hero with a "Your First Visit, Made Easy" card
2. New-patient offers
3. Services (4 photo cards plus 16 services)
4. Why Belmont
5. "Typical office vs. Belmont" comparison
6. Doctors and awards
7. Same-day CEREC crowns, with the in-office milling video
8. Insurance, reviews and office tour
9. First-visit steps and what to bring
10. FAQ, location and final CTA

**Emergency page** (phone-first, with red pulsing call buttons):
1. Hero with a "What's going on?" card: 8 tap-to-call problem buttons
2. 8 emergencies we treat
3. First aid ("What to do right now") with a warning box for when to go to the ER or call 911
4. Emergency treatments: extractions, root canal, CEREC, incision and drainage, pulpotomies, bonding
5. The 6-step emergency visit
6. Reviews, led by the real "got us in within 2 hours" review
7. Why Belmont and offers
8. Doctors, awards, insurance and office tour
9. FAQ, location and final CTA

**Desktop vs. phone:** desktop gets 3D tilt with light glare on the cards, a parallax hero card, scroll-reveal
animations and a floating photo. On phones, the card grids turn into swipe carousels with arrows and dots, and some
of them advance on their own until touched. The buttons are 56–66 px tall.

## Brand match

The colours, fonts and buttons come from belmontdentistry.com's own theme. They are:

| Token | Value | Used for |
|---|---|---|
| Gold | `#DBAA4B` | Buttons and accents |
| Dark brown | `#2F1B00` | Dark sections |
| Near-black | `#1E1B16` | Header and the ink sections |
| Cream | `#FAF5ED` | Light bands |
| Red | `#C70000` | The emergency page's urgent accent (also from the site theme) |

**Fonts:** **Gloock** for headings and **Karla** for body text, the same pair the site uses. All photos, the logo and
the video are the practice's own, taken from the Scottsdale pages of the site. Nothing is stock.

## Keywords (Quality Score)

- **New patients:** the H1 is "Scottsdale's Family Dentist", and the title is "Scottsdale Dentist Near Me". The copy works in North Scottsdale, Old Town, dentists in Scottsdale AZ, family dentist, dental care services, dental clinic for no insurance, general practice dentist and local dentist.
- **Emergency:** the H1 is "Emergency Dentist in Scottsdale. Get Seen Today." The page covers same-day / emergency dental care, emergency tooth extraction and Tooth Extraction Scottsdale. North Phoenix is covered in the location text and an FAQ.

## SEO / tracking

- **Search indexing:** `noindex, follow` keeps the pages out of organic search, which Google Ads doesn't need. The canonical tag points to the existing `/lp/...` URLs.
- **Structured data:** `Dentist` JSON-LD with `aggregateRating` (4.9 / 699), 4 `Review` items, hours, the address, the doctors and the services. There is also an `FAQPage` block. Google doesn't show review stars for a business's own markup, so this won't add stars to search results. It describes the rating that's on the page.
- **Google Tag Manager:** container **GTM-PKC6XXJ** is on both pages and both standalone copies. The script is the first thing in `<head>` and the `<noscript>` iframe is the first thing in `<body>`, as Google recommends. The ID is `GTM_ID` in `build.py`.
- **Events:** `assets/js/lp.js` pushes `click_to_call`, `click_book_online` and `click_directions` to `dataLayer` (also `gtag` / `fbq` if present). Each includes `lp_location`, which says which button was clicked. In GTM, create Custom Event triggers on those event names for your Google Ads conversion tags. Optionally, fill in `ADS_CONVERSION_ID` / `LABEL_CALL` / `LABEL_BOOK` in `lp.js` to fire conversions directly instead.

## Please confirm before running ads

1. **Offers.** No price-based offer for Scottsdale is published anywhere on the site. The only priced plan ($349/yr) is on the Phoenix page, so I didn't use it. The offer cards are:
   - same-day visits
   - the Belmont Dental Plan (no price shown)
   - a free benefits check
   - CareCredit

   If Scottsdale has a new-patient special or a price for the Belmont Dental Plan, send it and I'll add it.
2. **"Super Practice & Patient's Choice" badge.** This comes from the current landing page (it's a directory profile badge). Keep it only if it's still current.
3. **Free parking.** This comes from the current landing page's features list. "Free Uber rides" was also on that list, but I left it out. Confirm both.
4. **Rating.** 4.9★ from 699 Google reviews was read from the site's own Google review feed in October 2026. It's hard-coded, so update `RATING` / `REVIEW_COUNT` in `build.py` from time to time.
5. **Reviews.** 8 verbatim 5★ Google reviews of the Scottsdale office, reproduced exactly as written, spelling included.
6. **Hours.** Friday and Saturday run on alternate weeks. The live status works in Arizona time and tells visitors to call to confirm on those days.

## Editing

All copy lives in `build.py` (Python 3.12+). Edit it, then run:

```bash
python3 build.py
```

That regenerates both pages and both standalone copies. Styles are in `assets/css/belmont.css` and behaviour is in
`assets/js/lp.js`.

## Preview locally

```bash
python3 -m http.server 8000
```

Then open http://localhost:8000/new-patients-scottsdale.html. Use a server so the map and videos load.
