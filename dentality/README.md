# Dentality Family Dentistry — Google Ads Landing Page

A conversion-focused Google Ads landing page for **Dentality Family Dentistry** (Katy, TX),
rebuilt from the practice's existing `/lp/general-dentist/` page.

```
dentality/
  index.html                 the landing page (self-contained, deploy anywhere)
  assets/css/style.css       design tokens + every component
  assets/js/main.js          tracking hooks, scroll reveals, hours, accordion
  assets/img/                the practice's own photography, logo and icons
```

Preview locally with a server (the map embed needs `http://`):

```bash
python3 -m http.server 8000     # then open http://localhost:8000/dentality/
```

---

## Before you run traffic — required setup

### 1. Google Ads conversion tracking

Paste your Google tag into the `<head>` of `index.html`, then fill in the three values at the
top of `assets/js/main.js`:

```js
var ADS = {
  conversionId: 'AW-XXXXXXXXX',
  labelCall:    '...',   // click-to-call conversion label
  labelBook:    '...'    // book-online conversion label
};
```

Events already fire on every CTA, to `gtag`, `fbq` and `dataLayer`:

| Event | Fires on |
|---|---|
| `click_to_call` | every `tel:` link — header, hero, service card, ribbon, insurance, FAQ, location, final CTA, sticky mobile bar |
| `click_book_online` | every link to `book.modento.io` — 12 of them |
| `click_directions` | the Google Maps links |

Any element can be instrumented by adding `data-track="call|book|directions"`.

### 2. Decide on indexing

The page ships with `<meta name="robots" content="noindex, nofollow">` so it does not compete
with the main site organically. Google Ads serves it either way — remove the tag only if you
want it indexed.

**There is no lead form.** The two conversion paths are the phone and the practice's own
scheduler at `https://book.modento.io/dentality-family-dentistry/reason-for-visit` — the same
one the main website uses.

---

## What changed, and why

The original page ran: hero → trust → **three promotional offers** → why us (9 cards) →
doctors → services (6 cards) → comfort menu → insurance → FAQ → hours → reviews → CTA.

| Change | Reason |
|---|---|
| **Offers moved out of position 3** | Implants at `$99/mo` and `$1,000 off Invisalign` are not what a "dentist in Katy" searcher wants, and a discount block that high made the page read as a coupon site. Only the `$69` new-patient exam survives, inside the affordability section where it answers a real objection. |
| **Reviews moved up, above insurance** | They were second-to-last on the original. Proof now lands before the page asks anyone to think about money. |
| **9 "why us" cards → 6 numbered rows** | The nine overlapped heavily (three of them were about the same first visit). Six stronger claims in an asymmetric editorial list, next to a sticky photo. |
| **Comfort menu promoted to a full dark section** | It was a small grid two-thirds down. It is the single best anxiety-reducer the practice has, so it now gets a full-bleed navy section and a layered image pair. |
| **Services: 6 identical cards → one featured + 4 + 1 wide** | Preventive care is the acquisition service, so it leads at 2× size with a photo; emergency closes the block full-width because it is a phone conversion, not a booking one. |
| **New: 3-step first-visit section** | The original never explained what actually happens, which is the most common reason a nervous patient does not book. |
| **New: sticky mobile call/book bar** | Most Google Ads dental traffic is mobile; the CTA is now always on screen. |
| **Navigation cut to 5 anchors** | It is a landing page, not a website. No outbound links except the booking scheduler and Google Maps. |

Section order now: hero → trust strip → why Dentality → the experience → services → ribbon CTA
→ doctors → reviews → insurance → first-visit steps → FAQ → location → final CTA.

No two consecutive sections use the same layout: split, strip, asymmetric-with-sticky-image,
dark layered, editorial grid, ribbon, portrait-led, featured-quote, split card, stepped, two-column
accordion, overlapping card + map, centred.

---

## Design system

Every colour is sampled from the practice's own assets rather than approximated.

| Token | Value | Taken from |
|---|---|---|
| `--navy-950` … `--navy-700` | `#04182e` → `#14456d` | the logo wordmark and the team's scrubs |
| `--cyan` | `#25a9e0` | the logo's D-and-tooth mark |
| `--cyan-600` / `--cyan-700` | `#0c79ac` / `#075e88` | darkened for AA-contrast CTAs |
| `--walnut` / `--walnut-soft` | `#a2652f` / `#c08a4e` | the walnut slat walls in the office photos |
| `--sand` / `--sand-deep` | `#f8f3ec` / `#efe5d7` | warm neutral, keeps the page off "medical template" blue |
| `--ink` / `--ink-soft` / `--ink-mute` | `#16283a` / `#4d6072` / `#5e6d7e` | all ≥ 4.5:1 on both white and sand |

Type is **Plus Jakarta Sans** (400–800) with **Instrument Serif** italic used only for editorial
moments — the pull quote, the featured review, and the section numerals. Two families, nothing else.

The arch shapes on the hero, "why", experience and doctor images echo the "D" of the logo mark.

---

## Accuracy notes

Everything on the page comes from Dentality's own website. Nothing was invented — no awards,
statistics, certifications, review counts, years of experience or guarantees.

- **Office hours** are the practice's real hours: Mon/Wed 9–6, Fri 9–5, Sat 9–3, Tue/Thu/Sun closed.
  Today's row highlights automatically, computed in **Katy time** (`America/Chicago`), not the
  visitor's timezone.
- **⚠️ One conflict was resolved.** The original landing page said *"Open Saturdays 8 AM – 2 PM"*
  in its body copy but listed *Saturday 9:00 AM – 3:00 PM* in its own hours table — and the main
  website also says 9–3. **This page uses 9 AM – 3 PM everywhere.** Please confirm which is right;
  if it is 8–2, search `9:00 AM – 3:00 PM`, `9 AM – 3 PM` and `9–3` in `index.html`.
- **Phone** is `(281) 407-8555`, the tracking number on the existing landing page. The main
  website lists `281-712-2288`.
- **Reviews** are the three real patient reviews from the practice's page, quoted verbatim, with
  the same first-name attribution.
- **Rating**: `4.9` is shown as "average patient rating", matching the original page. The
  `Dentist` schema block deliberately **omits `aggregateRating`** — Google requires a verified
  `reviewCount` alongside it, and no review count is published. Add it once you have the real
  count from the Google Business Profile.
- **Doctor bios, credentials and schools** are the practice's own wording, lightly tightened.
- Comfort-menu items and the "additional fees apply" caveat on nitrous oxide are unchanged.
- The `$69` exam-and-X-rays offer is presented as a self-pay option, which is how the original
  frames it. The implant and Invisalign promotions are deliberately not on this page.

---

## Technical

- **~287 KB total transfer** on first desktop load, including fonts and all above-the-fold imagery.
- Every image is the practice's own photography, re-encoded to WebP and served locally. 17 of 19
  images are lazy-loaded; the hero is preloaded with `fetchpriority="high"`.
- **No JavaScript libraries.** ~90 lines of vanilla JS, deferred. The page is fully usable with
  JS disabled — the FAQ uses native `<details>`, and reveals default to visible.
- Semantic HTML5, single `<h1>`, no heading-level skips, every image has alt text, a skip link,
  visible focus rings, and `prefers-reduced-motion` honoured.
- No horizontal overflow at 390 / 768 / 1024 / 1440. No mobile tap target under 40 px.
- `Dentist` and `FAQPage` JSON-LD, with address, hours, service list and the three clinicians.
