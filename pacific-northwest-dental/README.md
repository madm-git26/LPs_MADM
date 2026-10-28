# Pacific Northwest Dental — Dental Implants Landing Page (Beaverton, OR)

A redesign of the earlier `pacific-northwest-dental-implants-lp` page. Every section, price, claim, FAQ,
review, phone number and link from that page is carried over unchanged; the new design adds a 3D
implant animation, 3D procedure illustrations and a YouTube video section.

| File | Use it when |
|---|---|
| `dental-implants.html` + `assets/` | You can upload the page **and** its `assets/` folder together (fastest loading). |
| `dental-implants-standalone.html` | You need one self-contained file (page builder / custom-code block). Every image and video is embedded. Rebuild with `python3 build_standalone.py`. |
| `dental-implants-photo-hero.html` (+ `assets/`) | **Still-image hero version:** the same page, but the hero shows a still 3D implant image instead of the 3D video (see below). |
| `dental-implants-photo-hero-standalone.html` | The still-image hero version as one self-contained file (3.7 MB — no video). |

### Still-image hero version

Identical to the main page (same text, form, phone number, links and sections) except the hero: the 3D
video and its pause button are replaced by a still 3D render of a dental implant in an "exploded" view —
ceramic crown, abutment with a brand-blue collar and threaded titanium implant — floating on black with
blue rim light, a soft brand-blue glow, light particles and a glowing ring at the implant platform.

- Desktop: the upright implant sits in the gap between the headline and the **Get Pricing Instantly**
  form, with a dark shade behind the headline for legibility. On very wide screens the image stays
  1500 px wide and fades into the black hero at its edges.
- Phones and tablets: the headline sits above a tilted (diagonal) version of the same render, followed
  by the CTAs and the form — the same order as the video version.
- Files: `assets/img/hero/hero-photo.webp` (desktop, 2400×1500) and `hero-photo-mobile.webp`
  (phones/tablets, 960×842). Rendered for this page from the same original 3D model as the rest of the
  artwork (`3d-source/hero3d.js`, `hero3d.html`, `hero3d-render.js`; glow and particles added by
  `hero-composite.py`) — no stock imagery, so no licensing restrictions.
- The page is generated from `dental-implants.html` by `make_photo_hero.py`, so edits to the main page
  carry over: run `python3 make_photo_hero.py && python3 build_standalone.py`.

## Kept exactly as on the previous page

- Call tracking number **(971) 306-5712** → `tel:9713065712` on every call button (header, hero, form card, pricing cards, 3D section, process, what-to-expect, doctor, financing, location, final CTA, sticky mobile bar).
- Every **Book Online** button → `#pricing-form` (the hero "Get Pricing Instantly" form).
- Lead form: the All-in-One Dental implant quiz iframe (`forms.allinone.dental/form/159a64b0-…`, 610 px) + its `iframeresize.js`. The iframe carries `id="embededFormIframe"`, which that script needs to resize it.
- Directions / map, Google reviews link, Privacy, Terms, Make a Payment, logo → same URLs as before.
- Canonical, `Dentist` + `FAQPage` structured data — unchanged.

## Google rating banner (hero, both versions)

- The first thing in the hero: Google "G", **4.9**, five gold stars filled to the exact rating and
  **811 Google reviews**, linking to the Google Business Profile
  (https://maps.app.goo.gl/ed1gZ21XjdENS5Ns9, place ID `ChIJqR93058OlVQRo_F-q8nS7M0`).
- The same numbers are in the `Dentist` JSON-LD as `aggregateRating` (plus `hasMap` → the profile).
- The page ships with the figures read from Google on 28 Oct 2026. **Live mode:** create a Google Maps
  Platform API key with *Maps JavaScript API* and *Places API (New)* enabled, restrict it to this site's
  URL (HTTP referrers), and paste it into `apiKey: ''` in the page script (search for `G_PLACE`), then
  re-run `python3 make_photo_hero.py && python3 build_standalone.py`. The banner and the schema then
  update from Google after the page loads; each visitor's browser caches the result for 12 hours.
  Google bills these lookups (Place Details), so watch the usage in the Cloud console.
- Without a key the banner simply shows the shipped figures — update the numbers in the banner and the
  JSON-LD (or ask for a refresh) when the review count grows.
- Search: this page is `noindex`, and Google does not show review stars for a business's own
  `LocalBusiness`/`Dentist` markup, so the schema will not create stars in Google results; it describes
  the rating shown on the page.

## Tracking & SEO tags (both versions, and both standalone files)

- Title: `Dental Implants in Beaverton, OR | All-On-4 & Snap-In Dentures`
- Meta description: `Missing teeth? Dr. Ryan Bradley offers All-On-4, snap-in implant dentures and single tooth
  implants in Beaverton, OR. Get pricing instantly. Monthly payments with approved credit.`
- `<meta name="robots" content="noindex, follow">` — the landing page stays out of search results, links
  are still followed.
- Google Tag Manager container **GTM-KXLHG72**: the `<script>` snippet is at the top of `<head>` and
  the `<noscript>` iframe is the first thing inside `<body>`, as Google recommends.

## Brand

Colours and fonts match pacificnorthwestdentist.com: black `#000` / charcoal `#2D2D2D` backgrounds,
bright blue `#0397D6` buttons and accents, white and `#F6F6F6` light bands, gold `#F7B727` rating
stars, Montserrat headings and Lato body text. All text, headings and buttons are centre-aligned.

## Sections

1. Top bar + sticky header (Pricing · 3D Implant · Process · Dr. Bradley · Reviews · FAQ)
2. **Hero** — full-bleed 3D implant animation behind the headline and the **Get Pricing Instantly** form (desktop 16:9 cut). On phones the headline sits above the 4:5 video, followed by the CTAs and the form; the NewMouth "Best Dentist in Portland 2023" award badge sits under the trust chips (also shown beside the logo in the footer, `assets/img/award-newmouth-2023.webp`)
3. Value points
4. Pricing — All-On-4 feature card + snap-in (2 / 4 implants), 3-tooth bridge, single tooth — each with a clinical-style 3D render on white (glassy translucent gum with the implants visible inside, blue-collared abutments, gold snap-in attachments, natural teeth floating above the jaw; source `3d-source/clinical.js`)
5. Why choose our implant team
6. **Inside a dental implant (3D)** — on desktop the crown, abutment and titanium implant assemble as you scroll; on phones the animation is removed (its frames never download) and the section shows the three parts + call CTA
7. **The implant process in 3D** — tablet & desktop: the section pins while you scroll and a 48-frame 3D sequence plays the whole procedure (3D scan + planned implant → implant screws in → bone heals → abutment → crown), with the active step highlighted and a progress bar (`assets/img/3d/proc/`, rendered by `3d-source/procseq.js`). Phones keep five square tiles in two rows (3 + 2) and never download the frames
8. What to expect (the original 3 steps, with a scroll progress line)
9. Dr. Ryan Bradley
10. **Videos** — the practice's YouTube videos (load only when clicked, via youtube-nocookie)
11. Reviews (the same 7 Google reviews, auto-scrolling)
12. Financing (CareCredit, Proceed Finance) + insurance logos from the main site
13. FAQ, location & hours, final CTA, footer, sticky mobile call/book bar

## The 3D artwork

All 3D video and images were rendered for this page from an original procedural model
(`3d-source/`, three.js) — no stock footage, so there are no licensing restrictions.

- `assets/video/pnw-implant-3d.(webm|mp4)` — 1920×1080, 13 s seamless loop (desktop)
- `assets/video/pnw-implant-3d-mobile.(webm|mp4)` — 864×1080 portrait loop (phones)
- `assets/video/hero-poster*.jpg` — first frame (shown instantly), `hero-still*.jpg` — finished tooth (shown to visitors with reduced motion turned on)
- `assets/img/3d/` — procedure stills, treatment-option renders, 40-frame assembly sequence

The hero video only downloads the cut that fits the screen, plays muted, pauses when off screen and
has a pause button. All animation respects the visitor's "reduce motion" setting.

To re-render (e.g. new colours): `cd 3d-source && npm i three@0.169.0 playwright`, serve the folder
(`python3 -m http.server 8765`), then run `node seq.js …` / `node batch.js` (arguments are documented at the top of each script) and
`./encode.sh <frames_dir> <out_name>` to build the seamless-loop video.
