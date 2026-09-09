# Justin Dental and Braces — Google Ads Landing Page

A conversion-focused Google Ads landing page for **Justin Dental and Braces** (Justin, TX),
built with an EN/ES language toggle, per the practice's family-owned, bilingual positioning.

The design system (tokens, layout, and every component — arch-shaped imagery, the numbered
"why us" list, the doctor lead card, the review grid, the overlapping map card, etc.) is ported
directly from the **Dentality Family Dentistry** build (`dentality/`, a sibling project on this
repo) so the two landing pages share one consistent visual language across the client portfolio.
Only the palette (navy + teal, sampled from this practice's own logo, in place of Dentality's
navy + cyan) and the content differ. Justin's own mandatory features — the EN/ES toggle, the
"We Speak Spanish" messaging, Cherry financing, the Dental Savings Plan, and the hero video — are
folded into that same component system rather than bolted on separately.

```
justin-dental/
  index.html                 the landing page (deploy the whole folder)
  justin-dental-landing-page.html   standalone build — same page, CSS/JS/images/video inlined
  assets/css/style.css       design tokens (ported from Dentality) + every component
  assets/js/i18n.js          EN/ES text dictionary + language toggle
  assets/js/main.js          tracking hooks, scroll reveals, FAQ, floating CTA, hero video
  assets/img/                the practice's own real photography and logo
  assets/video/              the practice's own intro clip, used as the hero background
```

Preview locally with a server (the map embed needs `http://`):

```bash
python3 -m http.server 8000     # then open http://localhost:8000/justin-dental/
```

---

## ⚠️ Needs verification before launch

The practice's main website (`justindentalandbraces.com`) sits behind a bot-protection
challenge (SiteGround's `sgcaptcha`) that blocked every automated access attempt during this
build — curl, a headless browser, and the Wayback Machine were all refused or blocked by this
session's own network policy. Everything on this page was instead sourced from the practice's
own accessible content: a sister marketing site on the same domain family
(`affordablebracesjustin.com`, confirmed as the same practice — identical phone number and
address), search-engine snippets, and directory listings (Yelp, BBB, Healthgrades). That covers
real doctors, real reviews, real photos, and confirmed NAP — but a few things below could not be
verified and need your input before this goes live:

1. **Cherry financing link — genuinely not found anywhere.** Not on the accessible sister site,
   not in any indexed snippet. Per your own instruction not to invent one, the "Check Your
   Financing Options" button in the Financing section currently calls the office
   (`tel:+19402422022`) instead of linking to Cherry. Search for `data-cherry-url=""` in
   `index.html` — once you have the real pre-qualification URL, put it there and change that
   button's `href` from the phone number to it.
2. **Insurance carrier list.** Only **Aetna** could be independently confirmed (via search
   snippets). The Insurance section says "Aetna" plus "most major PPO dental plans" rather than
   listing carriers I couldn't verify. If the practice accepts other named carriers, add them.
3. **Dental Savings Plan pricing.** Confirmed structurally (membership-based, no pre-existing
   condition limits, no annual cap, no waiting periods, includes exams/cleanings/X-rays) but the
   actual membership price was not accessible. The page says "Call our office for current
   membership pricing" rather than a number — fill it in if you'd rather show it directly.
4. **Google review count.** "1,000+" is corroborated by an independent search result describing
   the practice as having over 1,000 five-star Google reviews, but I could not open the live
   Google Business Profile to get an exact, current count. Confirm and update if you have a more
   precise figure.
5. **Tracking IDs.** `assets/js/main.js` has an `ADS` object at the top with empty placeholders
   for your GA4 Measurement ID, Google Ads Conversion ID, two conversion labels, and a GTM
   container ID — fill these in, then paste your actual GA4/GTM snippet into `index.html`'s
   `<head>`.
None of the above were guessed or invented; they're either sourced generically and flagged, or
left as an honest gap with a working fallback (calling the office) rather than a broken link.

There is no appointment request form or online booking widget on this page — every "Schedule"
CTA (hero, header, ribbon, FAQ, floating CTA, sticky mobile bar, footer, final CTA) calls the
office directly at `tel:+19402422022` instead.

---

## What's real, and where it came from

- **Both doctors are real**, with their own real bios: **Dr. Amee Pathak** (12+ years, Boston
  University's Henry M. Goldman School of Dental Medicine) and **Dr. Ankit "Andy" Shah**
  (orthodontist, 10+ years in the Metroplex, Master of Science in Orthodontics from St. Louis
  University, member of the American Association of Orthodontics and Texas Association of
  Orthodontists). Their portrait photos, the hero's doctors-together photo, the logo, and the
  hero background video were all supplied directly by the practice/agency rather than sourced
  during the site crawl — see "Hero video" below for how the clip was prepared.
- **The team photo** is a genuine staff photo from the practice, including Dr. Shah.
- **All three reviews are real**, quoted from the practice's own testimonials page: Laura C.,
  "Dr Green's C.", and kintu l.
- **The logo is the practice's real logo**, including its own tagline — "Trust • Integrity •
  Compassion" — which the footer reuses.
- **NAP is confirmed**: 815 W 1st St Ste B, Justin, TX 76247 · (940) 242-2022 ·
  office@justindentalandbraces.com · Mon–Fri 9 AM–6 PM, Sat/Sun closed.
- **Surrounding communities** (Justin, Rhome, Ponder, Northlake, Boyd, Newark, Pecan Acres,
  Robson Ranch, Haslet, Decatur) were given directly and Decatur is independently confirmed —
  the practice runs a dedicated `affordable-braces-decatur-tx` page.
- **Before/after and treatment photos** (braces, Invisalign, oral surgery model) are the
  practice's own marketing images, reused here for the general dentistry campaign this page is
  built for rather than only the orthodontics campaign they originally accompanied.

## Deliberately excluded

Nothing was fabricated to fill a gap. Where real information wasn't accessible, the copy says so
generically (e.g., "most major PPO dental plans" instead of a fabricated carrier list) rather than
inventing specifics. No awards, certifications, statistics, or guarantees appear anywhere on the
page, per your brief.

---

## The EN/ES language toggle

`assets/js/i18n.js` holds a single Spanish dictionary keyed to `data-i18n` attributes throughout
`index.html`. Clicking **ES** swaps text in place — there is no duplicate Spanish copy of the page
sitting in the DOM, and the choice persists across the visit via `localStorage`. NAP, the brand
name, and both doctors' names are left untranslated in both languages, per your instruction. The
"WE SPEAK SPANISH" chip in the header only shows for English-reading visitors — it would be
redundant once the whole page is already in Spanish.

The sticky mobile bar's "Español" button is a quick in-place toggle (not a link to the Spanish
section) so a mobile visitor never leaves the page to switch languages.

---

## Hero video

The hero background is a 7-second clip of the practice's own intro video (Dr. Amee Pathak
introducing herself, following the brand's blur-and-logo open), supplied directly rather than
sourced during the site crawl. It's cut from seconds 3–10 of the original clip — the first 3
seconds of the blur-in open are trimmed off so the loop gets to the logo and the doctor faster.

- Muted, looped, `playsinline`, with a fresh 0.4s fade in (at the new start) and a 0.5s fade out
  so the loop point isn't a jump cut. No audio track at all -- it's stripped at encode time since
  the video is always muted.
- Encoded to both WebM/VP9 (`assets/video/hero.webm`, served first) and H.264 MP4
  (`assets/video/hero.mp4`, fallback for browsers without VP9 support, mainly older Safari) --
  about 615KB combined.
- **The source clip's own burned-in captions and lower-third graphic are permanently covered**
  with a solid navy bar baked into the video at encode time, not just a CSS overlay. They were
  written to accompany the clip's original audio, which never plays here since the hero video is
  muted -- left in, "(upbeat music)" would show up as a caption for sound that isn't playing. A
  CSS-only fix (a bottom gradient) was tried first but proved unreliable, since how much of the
  frame is actually visible shifts with hero height and viewport width; baking it into the pixels
  makes it correct regardless of layout.
- `assets/js/main.js` only injects a `<source>` and calls `.load()` on viewports ≥861px when
  `prefers-reduced-motion` is off -- confirmed zero network requests for either video file on a
  390px viewport. Everyone else (mobile, reduced-motion) sees the static poster
  (`assets/img/hero-poster.webp`, the doctors-together photo) with no video downloaded at all.
- The hero video and its poster now live inside `#hero-media` (`.hero__art-main`), the same
  arch-shaped image container Dentality uses for its hero photo -- the video simply fades in over
  the poster once it's ready to play (`.has-video`), so the layout is identical to Dentality's
  hero on a page with no video at all.

To re-cut the clip (a different window, or a different bar position) from the original
source, the exact command used was:

```bash
ffmpeg -ss 3 -i <source.mp4> -t 7 -an \
  -vf "scale=1280:720,drawbox=x=0:y=504:w=1280:h=216:color=0x071b30@1.0:t=fill,fade=t=in:st=0:d=0.4,fade=t=out:st=6.5:d=0.5" \
  -c:v libx264 -profile:v main -pix_fmt yuv420p -crf 26 -preset slow -movflags +faststart \
  assets/video/hero.mp4
# then swap -c:v libx264 ... for "-c:v libvpx-vp9 -crf 32 -b:v 0 -deadline good -cpu-used 2" -> hero.webm
```

---

## Design system

Ported from the Dentality Family Dentistry build (`dentality/assets/css/style.css`) so both
landing pages share one component library — same tokens structure, same section patterns
(`.hero__art-main` + `.hero__stamp` + `.hero__badge`, the numbered `.why__list`, `.doc-lead` /
`.doc-row`, `.review--lead` / `.review--sm`, `.ins__points` / `.ins__card`, the overlapping
`.loc__card`, etc.), re-colored to this practice's own logo:

| Token | Value | Direction |
|---|---|---|
| `--navy-950` … `--navy-700` | `#071b30` → `#1c4368` | deep navy, sampled from the logo |
| `--cyan` / `--cyan-600` / `--cyan-700` | `#17a2a2` / `#128585` / `#0c6e6e` | the logo's teal accent |
| `--walnut` / `--walnut-soft` | `#d9752c` / `#e69a5c` | warm accent for eyebrows, numerals and the "We Speak Español" stamp |
| `--sand` / `--sand-deep` | `#f4f7f8` / `#e9f1f1` | light supporting tone for alternating sections |

Headings use **Plus Jakarta Sans**, with **Instrument Serif** italic for the pull-quote and step
numerals — the same pairing as the Dentality build. Arch-shaped imagery (`--arch` token),
pill buttons, and moderate corner radius throughout.

---

## Technical

- Semantic HTML5, single `<h1>`, no heading-level skips, alt text on every image, a skip link,
  visible focus rings, `prefers-reduced-motion` honoured.
- Scroll reveals are gated behind a `js` class added by an inline script, so the page renders
  fully with JavaScript disabled — verified: with JS off, all 32 reveal elements are visible and
  the FAQ (native `<details>`) works normally.
- No horizontal overflow at 360 / 390 / 768 / 1024 / 1440 / 1920px. Every tap target is at or
  above the 44×44px minimum the brief specifies.
- `Dentist` and `FAQPage` JSON-LD, with real NAP, hours, doctors and service list.
- **No appointment form.** Every "Schedule" / "Request an Appointment" button on the page links
  straight to `tel:+19402422022` — there's no lead-capture form or booking widget to wire up a
  backend for.
- `data-track` attributes fire `phone_click`, `appointment_click`, `financing_click`,
  `language_es`, `directions_click`, and `review_click` events to `dataLayer`
  and, once configured, to `gtag`. Fill in the `ADS` object at the top of `assets/js/main.js` and
  paste your GA4/Google Ads tag into `index.html`'s `<head>`.
