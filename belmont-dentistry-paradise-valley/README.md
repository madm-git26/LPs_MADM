# Belmont Dentistry Paradise Valley — Google Ads Landing Pages

These are new landing pages; this practice had none before. **Paradise Valley office only:** 15255 N 40th St, STE 141,
Phoenix, AZ 85032 (Floor 1, Greenway Professional Park). The content comes from
belmontdentistry.com/paradise-valley-az/ and its subpages: new patients, emergency dentistry, tooth extractions,
smile makeover, insurance & financing, the membership plan, both doctor pages and the office tour.

| Page | File |
|---|---|
| New Patient / General Dentist | `new-patients-paradise-valley.html` |
| Emergency Dentist | `emergency-dentist-paradise-valley.html` |
| Thank-you page (shared by both) | `thank-you-paradise-valley.html` |
| Single-file copies | `standalone/*.html` (CSS, JS and every image built in) |

## Links & numbers

- **Phone:** (480) 530-3812 (`tel:+14805303812`). This is the only number on the pages; the website's (480) 530-0492 is not used.
- **Book Online:** https://book.allinone.dental/complete-dental-care?referrer_id=4
- **Google Business Profile:** https://maps.app.goo.gl/zwTqk5W6PRVpaw7w6
- **Map:** the Google Maps embed used on the Paradise Valley page.
- **Hours:** Monday–Friday 8:00 am–5:00 pm; closed Saturday and Sunday. The live open/closed status uses Arizona time.
- **Tracking:** GTM-PKC6XXJ on all three pages. Click events (`click_to_call`, `click_book_online`, `click_directions`) and the thank-you page's `thank_you_view` event work the same as on Scottsdale and Peoria.
- **Robots:** `noindex, follow` on the landing pages, `noindex, nofollow` on the thank-you page.
- **No forms, no social links, copyright-only footer.**

## Content specific to this practice

- **Dentists:** Dr. Puneet Sandhu, DDS (UCLA, Spear Faculty Club) and Dr. Sugandha Mohan (BDS, advanced training at NYU, serving Phoenix since 2015).
- **Rating:** 4.9★ from **508** Google reviews, read from the site's Paradise Valley review feed in October 2026.
- **Reviews:** 10 verbatim Paradise Valley Google reviews. I left out reviews that name the previous owner or the old practice name.
- **Savings plan:** $349/year. It includes 2 check-ups, 1 emergency exam, 2 regular cleanings and all X-rays, plus 50% off Cone Beam CT scans and 20% off all services. This is the price published on the Paradise Valley membership page.
- **Spa-style first visit:** coffee bar, lavender, a hot towel, and forms available in English and Spanish (from the new-patients page).
- **Before/after cases:** the 4 smile cases shown on the Paradise Valley page.
- **Photos & video:** the office's own photos.
  - **New-patient hero:** the full office film (`Phoenix.mp4`), exactly as the website plays it in its Paradise Valley hero.
    - The page plays a compressed copy, `assets/video/hero-new-patients.webm` (1.9 MB instead of 9.8 MB).
    - If that copy isn't uploaded, the browser falls back to the original file on belmontdentistry.com, so the single-file download plays the video with nothing else uploaded.
    - The poster image is the website's own video thumbnail.
    - The film's opening shows the "Complete Dental Care" sign and door lettering, including the office's other phone number.
  - **Emergency hero:** still a shorter cut of the film that starts after those shots.
  - Neither page uses the CEREC milling clip, because the Paradise Valley page doesn't advertise same-day CEREC crowns.

## What's new in the design (Paradise Valley only)

These pages use the same Belmont design system as Scottsdale and Peoria. A separate motion layer
(`assets/css/pv-motion.css` + `assets/js/pv-motion.js`) adds:

- **3D rating coin.** A gold coin with the Google rating sits on the hero card and spins to show the Google logo on the back (desktop).
- **Floating 3D rings** orbit behind the hero card (desktop).
- **Sliding headline.** The H1 words slide up into place one by one.
- **Scroll progress bar.** A thin gold bar at the top of the screen.
- **Scroll effects:**
  - The hero text drifts and fades as you scroll, and the hero video slowly zooms.
  - The insurance and final-CTA backgrounds scroll with parallax.
  - Headings wipe in.
  - Cards flip up in 3D as they enter the screen.
  - Doctor and office photos wipe in.
- **Buttons:**
  - Each click sends a ripple from the point you tapped.
  - On desktop, large buttons pull slightly toward the mouse.
  - The main Book button has a soft glow pulse, and icons nudge on hover.
- **Count-up numbers** in the stats bar.
- **Before/after smile sliders.** Drag to compare. Each slider sweeps once when it first appears, to show it can be dragged. They are a swipe carousel on phones.

Everything respects the "reduce motion" accessibility setting. With JavaScript off, the page still shows all
content and every button works.

## Please confirm

1. **"Paradise Valley" naming.** The office address is in Phoenix (85032). The pages use "Paradise Valley" for the practice name, the headlines and the keywords, as the website does, and mention North Phoenix in the location copy.
2. **The $349 plan** is shown as a price, because the Paradise Valley membership page publishes it. Confirm it's still current.
3. **Same-day emergency appointments** are promised, because the Paradise Valley FAQ says "We offer same-day emergency appointments".
4. **Insurance wording** is "in-network with several PPO plans", as the Paradise Valley page says, not "most major PPO plans".

## Editing

All copy is in `build.py` (Python 3.12+). Rebuild after editing:

```bash
python3 build.py
```

The standalone new-patient page plays its hero video straight from belmontdentistry.com. For the emergency page's video,
upload `assets/video/` and set `VIDEO_BASE_STANDALONE` to that URL. Until then, the emergency hero shows the clinic
photo instead.
