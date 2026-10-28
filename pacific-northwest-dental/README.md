# Pacific Northwest Dental — Dental Implants Landing Page (Beaverton, OR)

A redesign of the earlier `pacific-northwest-dental-implants-lp` page. Every section, price, claim, FAQ,
review, phone number and link from that page is carried over unchanged; the new design adds a 3D
implant animation, 3D procedure illustrations and a YouTube video section.

| File | Use it when |
|---|---|
| `dental-implants.html` + `assets/` | You can upload the page **and** its `assets/` folder together (fastest loading). |
| `dental-implants-standalone.html` | You need one self-contained file (page builder / custom-code block). Every image and video is embedded. Rebuild with `python3 build_standalone.py`. |

## Kept exactly as on the previous page

- Call tracking number **(971) 306-5712** → `tel:9713065712` on every call button (header, hero, form card, pricing cards, 3D section, process, what-to-expect, doctor, financing, location, final CTA, sticky mobile bar).
- Every **Book Online** button → `#pricing-form` (the hero "Get Pricing Instantly" form).
- Lead form: the same LeadConnector survey `uC0cfDGqyeVb4o6D2QvG` + `form_embed.js`.
- Directions / map, Google reviews link, Privacy, Terms, Make a Payment, logo → same URLs as before.
- Title, meta description, canonical, `Dentist` + `FAQPage` structured data — unchanged.
- The `<!-- Add your GTM / call-tracking snippet here -->` placeholder is still in `<head>`.

## Sections

1. Top bar + sticky header (Pricing · 3D Implant · Process · Dr. Bradley · Reviews · FAQ)
2. **Hero** — full-bleed 3D implant animation (desktop 16:9 cut, phone 4:5 cut), headline, call/book CTAs, trust chips, and the **Get Pricing Instantly** form above the fold
3. Value points
4. Pricing — All-On-4 feature card + snap-in (2 / 4 implants), 3-tooth bridge, single tooth — each with its own 3D render
5. Why choose our implant team
6. **Inside a dental implant (3D)** — scroll-driven model: crown, abutment and titanium implant assemble as you scroll, with call CTA
7. **The implant process in 3D** — five 3D stages (plan → place → heal → abutment → crown)
8. What to expect (the original 3 steps, with a scroll progress line)
9. Dr. Ryan Bradley (+ Dr. John Worthington from the main site)
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
