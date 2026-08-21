# Everything Teeth Family Dental — Google Ads Landing Pages

Four conversion-focused landing pages for **Everything Teeth Family Dental** (Miami, FL), built to match
the live website's theme and aimed at a single goal: **new patient bookings.**

| Page | File | Language |
|---|---|---|
| General Dentist | `general-dentist-en.html` | English |
| General Dentist | `general-dentist-es.html` | Español |
| Emergency Dentist | `emergency-dentist-en.html` | English |
| Emergency Dentist | `emergency-dentist-es.html` | Español |

`index.html` is an internal preview hub linking to all four — it is **not** meant to receive ad traffic.

Phone number used on every page: **+1 (305) 404-6659** (`tel:+13054046659`).

---

## Before you run traffic — required setup

Everything else works out of the box. These two items need your input:

### 1. Google Ads conversion tracking

Paste your Google tag in the `<head>` of each page, then fill in the labels in `assets/js/lp.js`:

```js
ADS_CONVERSION_ID: 'AW-XXXXXXXXX',
LABEL_CALL: '...',   // click-to-call conversion label
LABEL_BOOK: '...',   // book-online click label
```

Events already fire on every page (to `gtag`, `fbq` and `dataLayer`):

| Event | Trigger |
|---|---|
| `click_to_call` | any `tel:` link — header, hero, video card, sticky mobile bar, final CTA |
| `click_book_online` | any link to `book.modento.io` — the header, hero, video card, offers, mobile bar |
| `click_directions` | Google Maps / directions link |

**There is no lead form.** The two conversion paths are the phone and the practice's own online
scheduler at `https://book.modento.io/everything-teeth` — the same one the main website uses. Every
"Book" CTA opens it in a new tab; every phone CTA dials (305) 404-6659.

### 2. Remove `noindex` if you want these indexed

Each page ships with `<meta name="robots" content="noindex, nofollow">` so the landing pages don't
compete with the main site in organic search. Google Ads serves them fine either way — remove the tag
only if you want them in organic results too.

---

## What's on the pages

### General Dentist
Hero with the `$159` new patient offer + the clinic video → trust bar → **full general dentistry service list**
(Preventive, Restorative, Cosmetic, Sedation & Emergency — 21 services) → why we're different →
Dr. Omar & Dr. Diana → team → **offers + Premium Patient Program + insurance/financing** → reviews →
first-visit steps → location & hours → final CTA.

### Emergency Dentist
Urgency-first. Red accent (`#FF2A13`, taken from the site's own theme), pulsing call button, live
open/closed status, and a call CTA repeated in five places:

- Top bar + sticky header (always visible)
- Hero — large pulsing **Call (305) 404-6659**
- Under the hero video (phone is the primary button on this page, booking is secondary)
- After the emergency-conditions grid
- After "why Miami trusts us"
- Location block + final CTA
- **Sticky bottom bar on mobile** (call + book, always on screen)

Content: 8 emergency conditions → *"What to do right now"* first-aid steps (with an ER-instead warning
for airway/bleeding/trauma cases) → why us → doctors → `$75` limited exam offer → reviews → hours.

### Both pages include
- **The clinic's own video**, in the hero where the form used to be — the same film that plays on the
  main website's homepage (`Everything-Teeth.webm`, 21s, 1280×720), with the site's own poster frame.
  It is muted, loops, and **only starts once it is actually on screen**, so a phone visitor who never
  scrolls past the headline downloads none of it. A play/pause button sits in the corner, a manual
  pause is never overridden by scrolling, and `prefers-reduced-motion` holds it on the poster frame.
- **Real reviews** — from the website and the practice's Google Business Profile, with the live
  **5.0 / 640+** aggregate and a link to the GBP listing. Spanish pages use the real Spanish-language
  Google reviews.
- **Doctor details** — real bios, education (FIU → LECOM) and specialties.
- **Team** — all five team members with real roles.
- **Payment plans & offers, compressed into one scannable block:**
  - 4 offer cards: `$159` new patient · `$75` limited exam · implants `$199/mo` · Invisalign `$199/mo`
  - Premium Patient Program: `$300` adult / `$175` child under 14 / `$200` each additional family
    member per year, what's included, and the 25–40% treatment discount
  - Insurance (all PPO, 100/80/50 coverage) · CareCredit® · in-house financing
- **No footer and no footer links** — just a bottom bar with the copyright line, per spec. The only
  outbound links anywhere are the Google Maps listing and the review link.

---

## Theme fidelity

Colours, fonts and button geometry were extracted from the live site's stylesheet, not approximated:

| Token | Value | Used for |
|---|---|---|
| `--navy` | `#00335D` | headings, phone button, dark sections |
| `--lime` / `--lime-dark` | `#A7DB2C` / `#7EAA15` | primary CTA + hover |
| `--blue` | `#2FA0FF` | hover accents, focus rings |
| `--sky` | `#E9F5FF` | light section backgrounds |
| `--ink` | `#272727` | body copy |
| `--urgent` / `--urgent-dark` | `#FF2A13` / `#A71000` | emergency page (also from the site theme) |

Fonts are the same four the site loads: **Instrument Sans** (headings + body, 600 weight,
`-0.035em` tracking), **Karla** (labels/secondary buttons), **Poppins**, and **The Nautigal**
(script accent). Hero headline is `65px` stepping down to `35px`, matching the site's own breakpoints.
Buttons are square-cornered, uppercase, `0.05em` tracking — same as the live site.

All images and the logo are the practice's own assets, served locally from `assets/img/`.

---

## Files

```
index.html                     internal preview hub
general-dentist-en.html        ┐
general-dentist-es.html        │ the four landing pages
emergency-dentist-en.html      │ (self-contained, deploy anywhere)
emergency-dentist-es.html      ┘
assets/css/theme.css           brand tokens + all components
assets/js/lp.js                video control, tracking, hours logic
assets/img/                    logo, photos, icons, video poster (from the live site)
assets/video/                  the clinic's own film, taken from the main website
build.py                       regenerates the four pages
content.py                     all copy, both languages
```

### Editing

Either edit the `.html` files directly, or edit `content.py` and run:

```bash
python3 build.py
```

Generating from `content.py` keeps the English and Spanish versions structurally identical — only the
strings differ — so a layout change lands on all four pages at once. Editing the HTML directly is fine
too; just know that a rebuild overwrites it.

### Preview locally

```bash
python3 -m http.server 8000
# then open http://localhost:8000/
```

Use a server rather than opening the files directly — the Google Maps embed and the video both need
`http://`. (If the map is ever blocked, the panel falls back to an address card with a Get Directions
button; if the video cannot play, its poster frame stays up with a play button.)

---

## Notes on accuracy

- **Office hours** are the practice's real hours: Mon/Wed/Thu 10:30 am–6:30 pm, Fri 7:30 am–3:30 pm,
  Tue/Sat/Sun closed. Today's row is highlighted automatically and an "open now / currently closed"
  status is computed in **Miami time**, not the visitor's timezone.
- The emergency page deliberately **does not claim 24/7 availability**, since the practice is closed
  three days a week. It says emergency appointments are welcome and to call as early in the day as
  possible — which is accurate and still converts.
- Review counts (640+) and the 5.0 rating reflect the Google Business Profile at build time. These are
  hard-coded, not live — refresh them in `content.py` periodically (`reviews_count`, `reviews_title`,
  `hero_rating`, and the `aggregateRating` in the schema block in `build.py`).
- The hero video is WebM, the only format the practice publishes it in. That covers Chrome, Edge,
  Firefox, Android, and Safari 14.1+ / iOS 17.4+. Anywhere it cannot decode, the poster frame shows
  instead — nothing breaks. If you want an MP4 fallback for older iPhones, drop
  `Everything-Teeth.mp4` into `assets/video/` and add a second `<source>` in `build.py`.
- The practice's main website lists **(305) 777-7774**. These landing pages use the tracking number
  **(305) 404-6659** you supplied, everywhere.

---

## Additional landing page — Precision Dental (Las Vegas, NV)

`precision-dental-lv-emergency.html` is a standalone, single-file emergency-dentistry landing page for
**Precision Dental**, 6545 S Fort Apache Rd Ste 110, Las Vegas, NV 89148 — phone **702-331-4444**
(`tel:7023314444`). It is self-contained (inline CSS/JS, remote images from precisiondentallv.com) and
unrelated to the Everything Teeth pages above, so it does not go through `build.py`.

**Animated hero headline.** The H1 reads `In Pain? / <rotating keyword> / Starts Right Here`, where the
gold script line cycles through eight emergency-dentistry keyword phrases every 2.8s: Fast Relief,
Emergency Dental Care, Tooth Pain Relief, Same-Day Treatment, Broken Tooth Repair, Knocked-Out Tooth
Care, Abscess & Swelling Care, Urgent Dental Care. To edit the list, change the `.kw` spans inside
`#kwRotator`; timing lives in `KW_INTERVAL`.

- All phrases sit in the DOM, so crawlers see every keyword; the rotator is `aria-hidden` and a
  visually-hidden sentence gives screen readers one clean H1.
- Rotation pauses on hover/focus of the hero and when the tab is hidden.
- `prefers-reduced-motion: reduce` disables the rotation (first phrase stays), the progress meter, the
  glow drift, the CTA pulse, and all scroll reveals.
- Each phrase is auto-fitted to one line at any viewport width, so the headline never reflows.

**Page sections:** hero → what counts as an emergency → 7 emergency types → 5-step visit process →
why timing matters → hours + after-hours note → emergency services → doctors → insurance → location →
reviews → "We're here when you need us most" CTA → 9-question FAQ → map → footer.

Structured data: `Dentist` (with hours, geo, `availableService`) + `FAQPage` covering all 9 visible FAQs.
Ships with `noindex, nofollow` like the other landing pages — remove it if you want organic indexing.

---

## Additional landing page — Shades Creek Dental (Homewood, AL)

`shades-creek-emergency-dentist.html` is a standalone, single-file landing page for **Shades Creek
Dental**, 1045 Broadway Park, Suite 101, Homewood, AL 35209 — phone **205-417-2750**
(`tel:2054172750`), booking at `https://www.shadescreekdental.com/book-an-appointment/`. Self-contained
(inline CSS/JS); it is not part of the `build.py` pipeline.

### Campaign intent

Built for the **high-value emergency** angle, not new-patient volume: the practice is deliberately down
from ~75 new patients a month to 30–50 with hygiene booked out two months, and wants emergencies as the
gateway to crowns, root canals, bridges, dentures and implants. On a $500–$1,000/month budget every
click has to count, so the page is phone-first (call CTA in the header, hero, every treatment block, the
sticky mobile bar and the footer) and carries no new-patient-special or cleaning/exam offer.

### Ad-group deep links

Each keyword cluster has its own on-page block with a stable anchor, so ads can land on the section that
matches the search term instead of the top of the page:

| Ad group | Landing URL |
|---|---|
| Emergency dentist / urgent dental care | `…#emergencies` |
| Broken / cracked / fractured tooth | `…#broken-tooth` |
| Broken, lost or fallen-out crown | `…#emergency-crown` |
| Same-day crown / CEREC | `…#same-day-crowns` |
| Emergency & urgent root canal | `…#root-canal` |
| Dentures (full, partial) & dental bridges | `…#replace-teeth` |

### Brand match

Colors and assets come from the live site: teal `#005E70`, light blue `#A8D3DB`, pale `#E4F1F4`.
Headings use Cormorant Infant (the site's display serif); body uses Hanken Grotesk as a free stand-in
for the site's Typekit `neuzeit-grotesk`. Header/footer logos are the site's own SVGs (both are
white/light artwork, so they sit on the teal header and dark footer). The team photo, Dr. MacBeth's
portrait and the emergency-service image are the practice's own files.

### Animation

All motion is scroll- or intent-triggered and fully disabled under `prefers-reduced-motion`:

- **Rotating H1 keywords** — eight emergency-service phrases on a 2.8s cycle with a progress meter.
  The rotator is `aria-hidden` with a visually-hidden H1 sentence for screen readers, pauses on
  hover/focus and tab hide, and auto-fits each phrase to a single line at any width.
- **Overlapping value cards** over the team photo (the layout the client asked for), lifting on hover.
- **Staggered grid reveals** at 60ms per item for the emergency, first-aid and differentiator grids.
- **Symptom triage chips** — tapping "my crown fell out", "severe toothache" etc. smooth-scrolls to the
  matching treatment block and flashes it, so ad traffic reaches the right answer in one tap.
- **Visit timeline** — the connector line draws left-to-right and the five step markers pop in sequence.
- Live open/closed badge and highlighted "today" hours row, resolved against America/Chicago.

### Hero video & required assets

The hero plays the practice's own b-roll instead of a still:

- `assets/video/shades-creek-hero.webm` — 1920×1080, 49s, 5.3 MB (supplied by the client)
- `assets/img/shades-creek-hero-poster.jpg` — poster frame, also the still shown when motion is off

Both are referenced with **relative paths**, so the HTML file must be deployed with the `assets/`
folder alongside it. The video is `muted`, `loop`, `playsinline`, `preload="metadata"`, and it pauses
automatically when the hero scrolls out of view or the tab is hidden. A 44px pause/play control sits on
the video (WCAG 2.2.2 — auto-playing motion longer than 5s needs a stop control). Under
`prefers-reduced-motion` or a `Save-Data` connection it never autoplays; the poster shows instead.

**Recommended before launch:** add an MP4/H.264 source next to the WebM for older iOS Safari. Drop the
file at `assets/video/shades-creek-hero.mp4` and add a second `<source>` above the WebM one. Without it
those devices fall back to the poster image, which is graceful but static.

### Header & logo

The header is near-black teal (`#002A33`) under a lighter teal info strip (`#0A7186`). The practice's
header SVG is a 57×66 icon and the footer SVG is a tall stacked lockup — neither reads as a name at
header size, so the header pairs the icon with a typeset wordmark in Cormorant Infant (the brand serif).
The full stacked lockup is still used in the footer, where it has room.

### Content sourcing

Emergency copy, the 8 emergency types, first-aid tips, "do not ignore dental pain", prevention and 8 of
the 11 FAQs are verbatim from `shadescreekdental.com/services/emergency-dentist/`. Dr. MacBeth's bio and
"Guided by Principle, Powered by Passion" are the client-supplied text. Reviews are real patient quotes
from the site. Technology claims (CEREC same-day crowns, 3D cone beam, digital X-rays, intraoral
cameras) come from the practice's "How We Are Different" page.

**Needs practice sign-off before running traffic:** the treatment-block detail and three added FAQs
(same-day crown replacement, re-cementing a crown that fell out, what happens when a tooth cannot be
saved) describe standard workflows for the technology the practice advertises, but they were written for
this page rather than lifted from the site.

Ships with `noindex, nofollow` like the other landing pages.
