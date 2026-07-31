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

Everything else works out of the box. These three items need your input:

### 1. Wire up the form (`assets/js/lp.js`)

```js
var CONFIG = {
  FORM_ENDPOINT: '',      // <-- set this
  ...
};
```

Set `FORM_ENDPOINT` to your form handler URL — Formspree, HubSpot, a Zapier catch-hook, or your own
endpoint. It receives a standard `multipart/form-data` POST with:

`name`, `phone`, `email`, `service`, plus `page` (which landing page) and `page_url`.

**Until you set it, no lead is lost:** the form validates, fires the conversion event, and shows
*"To lock in the soonest appointment, please call us now at (305) 404-6659."* It fails safe to the phone.

### 2. Google Ads conversion tracking

Paste your Google tag in the `<head>` of each page, then fill in the labels in `assets/js/lp.js`:

```js
ADS_CONVERSION_ID: 'AW-XXXXXXXXX',
LABEL_CALL: '...',   // click-to-call conversion label
LABEL_FORM: '...',   // form submit conversion label
LABEL_BOOK: '...',   // book-online click label
```

Events already fire on every page (to `gtag`, `fbq` and `dataLayer`):

| Event | Trigger |
|---|---|
| `click_to_call` | any `tel:` link — header, hero, sticky mobile bar, final CTA |
| `appointment_form_submit` | valid form submission |
| `click_book_online` | any link to `book.modento.io` |
| `click_directions` | Google Maps / directions link |

### 3. Remove `noindex` if you want these indexed

Each page ships with `<meta name="robots" content="noindex, nofollow">` so the landing pages don't
compete with the main site in organic search. Google Ads serves them fine either way — remove the tag
only if you want them in organic results too.

---

## What's on the pages

### General Dentist
Hero with `$159` new patient offer + inline lead form → trust bar → **full general dentistry service list**
(Preventive, Restorative, Cosmetic, Sedation & Emergency — 21 services) → why we're different →
Dr. Omar & Dr. Diana → team → **offers + Premium Patient Program + insurance/financing** → reviews →
first-visit steps → location & hours → final CTA.

### Emergency Dentist
Urgency-first. Red accent (`#FF2A13`, taken from the site's own theme), pulsing call button, live
open/closed status, and a call CTA repeated in five places:

- Top bar + sticky header (always visible)
- Hero — large pulsing **Call (305) 404-6659**
- After the emergency-conditions grid
- After "why Miami trusts us"
- Location block + final CTA
- **Sticky bottom bar on mobile** (call + book, always on screen)

Content: 8 emergency conditions → *"What to do right now"* first-aid steps (with an ER-instead warning
for airway/bleeding/trauma cases) → why us → doctors → `$75` limited exam offer → reviews → hours.

### Both pages include
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
assets/js/lp.js                form, validation, tracking, hours logic
assets/img/                    logo, photos, icons (from the live site)
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

Use a server rather than opening the files directly — the Google Maps embed needs `http://`.
(If the map is ever blocked, the panel falls back to an address card with a Get Directions button.)

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
- The practice's main website lists **(305) 777-7774**. These landing pages use the tracking number
  **(305) 404-6659** you supplied, everywhere.
