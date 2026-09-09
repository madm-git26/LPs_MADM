# Justin Dental and Braces — Google Ads Landing Page

A conversion-focused Google Ads landing page for **Justin Dental and Braces** (Justin, TX),
built with an EN/ES language toggle, per the practice's family-owned, bilingual positioning.

```
justin-dental/
  index.html                 the landing page (self-contained, deploy anywhere)
  assets/css/style.css       design tokens + every component
  assets/js/i18n.js          EN/ES text dictionary + language toggle
  assets/js/main.js          tracking hooks, scroll reveals, form, FAQ, floating CTA
  assets/img/                the practice's own real photography and logo
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
6. **Appointment form backend.** The form at `#contact-form` has no backend wired up — see
   "Technical" below.

None of the above were guessed or invented; they're either sourced generically and flagged, or
left as an honest gap with a working fallback (calling the office) rather than a broken link.

---

## What's real, and where it came from

- **Both doctors are real**, with their own real bios and photos: **Dr. Amee Pathak** (12+ years,
  Boston University's Henry M. Goldman School of Dental Medicine) and **Dr. Ankit "Andy" Shah**
  (orthodontist, 10+ years in the Metroplex, Master of Science in Orthodontics from St. Louis
  University, member of the American Association of Orthodontics and Texas Association of
  Orthodontists).
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

## Design system

| Token | Value | Direction |
|---|---|---|
| `--navy-950` … `--navy-700` | `#071b30` → `#1c4368` | deep navy, per brief |
| `--teal` / `--teal-700` | `#17a2a2` / `#0c6e6e` | soft teal accent |
| `--cta` | `#f0663e` | high-contrast orange for primary conversion actions — deliberately distinct from the navy/teal palette so it's unmistakable |
| `--sky` / `--sky-deep` | `#f2f7fb` / `#e7f0f7` | very light blue-gray supporting tone |

Headings use **Plus Jakarta Sans**, body copy uses **Inter** — the two families named in the brief.
Moderate corner radius (16px cards, pill buttons), subtle shadows, no heavy gradients.

---

## Technical

- Semantic HTML5, single `<h1>`, no heading-level skips, alt text on every image, a skip link,
  visible focus rings, `prefers-reduced-motion` honoured.
- Scroll reveals are gated behind a `js` class added by an inline script, so the page renders
  fully with JavaScript disabled — verified: with JS off, all 42 reveal elements are visible and
  the FAQ (native `<details>`) works normally.
- No horizontal overflow at 360 / 390 / 768 / 1024 / 1440 / 1920px. Every tap target is at or
  above the 44×44px minimum the brief specifies.
- `Dentist` and `FAQPage` JSON-LD, with real NAP, hours, doctors and service list.
- **The appointment form has no backend.** Submitting it validates the fields, fires the
  `form_submit` tracking event, and shows a client-side "Request Received" confirmation — but
  nothing is actually sent anywhere yet. Point `#appt-form`'s submit handler in
  `assets/js/main.js` at the practice's real intake (a Gravity Forms endpoint, a CRM webhook, or
  even a `mailto:`/Formspree fallback) before launch.
- `data-track` attributes fire `phone_click`, `appointment_click`, `form_submit`,
  `financing_click`, `language_es`, `directions_click`, and `review_click` events to `dataLayer`
  and, once configured, to `gtag`. Fill in the `ADS` object at the top of `assets/js/main.js` and
  paste your GA4/Google Ads tag into `index.html`'s `<head>`.
