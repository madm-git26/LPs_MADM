# Regency Court Dentistry of Boca Raton — Google Ads Landing Pages (Draft 1)

| Page | File | Primary CTA |
|---|---|---|
| General / New Patient | `regency-court-new-patient-dentist-boca-raton.html` | Book Online |
| Emergency Dentist | `regency-court-emergency-dentist-boca-raton.html` | Call (red), Book secondary |

Each page is **one self-contained HTML file** (inline CSS + JS, images hot-linked from the practice's
own website / CloudFront bucket, Google Business Profile and Unsplash). For WordPress: create a page with a
blank / canvas template and paste the whole file into a Custom HTML block, or upload the file as-is.

- **Ads phone:** (561) 979-2003 → `tel:+15619792003` everywhere (the main site lists (561) 998-0727 — not used)
- **Book Online:** `https://book.allinone.dental/regency-court-dental?referrer_id=3` (new tab)
- **GBP / directions:** https://maps.app.goo.gl/nfztTLTzJS8vadBk7 · embedded Google Map in the contact section
- **Google Tag Manager `GTM-N394H9F`** in the `<head>` + `<noscript>` iframe right after `<body>`
- **No forms, no social links, no footer menu** — copyright-only footer
- Robots: `noindex, follow` (same as the other LPs in this repo) — remove if you want them indexed

## Brand
Brand green `#9AC444` (the logo colour) on charcoal `#1E211C`, **Playfair Display** headings +
**Raleway** body — the same palette/type used on the practice's earlier Regency Court landing page, not the
current site's navy/gold redesign. Emergency page adds an urgency red `#E5484D` for call buttons only.

## Tracking (dataLayer events for GTM triggers)
`click_to_call`, `click_book_online`, `click_directions` (each with `lp` and `cta_zone` = section id),
`insurance_check` (`carrier`), and on the emergency page `triage_select` (`emergency`) and `exit_prompt_shown`.
Optional direct Google Ads conversion labels: `CONFIG` at the top of the page script.

## Facts used (all from the practice's site / GBP, Nov 2026)
- Google rating **4.6★ from 688 reviews** (GBP) — hard-coded; refresh periodically in `build.py` (`RATING`, `COUNT`)
- Hours Mon–Fri 8–5, Sat 8–2, Sun closed; live "open now / opens at…" status is computed in America/New_York
- Offers (site's Special Offers page): $69 new-patient exam & X-rays, FREE emergency exam & X-ray (new patients),
  FREE implant consult, $100 off whitening — with the site's own fine print
- Doctors: Dr. Naved Fatmi (UF; former Chairman/Vice Chair FL Board of Dentistry; Co-Chairman Larkin Hospital
  Dental Residency), Dr. Jordan Hekmati (periodontist & implant surgeon; NYU valedictorian, OKU),
  Dr. Yousof Sinjab (endodontist; Nova Southeastern). Team: Danielle Alvarez (CRDH), Gianna Rowe
- Reviews: real Google reviews (Richard Williams, Maria Trejo, Nicholas G., Elena Fontanazza), Google's review
  highlights, and the two "verified patient" testimonials from the practice website
- Insurance: the site doesn't publish a carrier list, so the page says "most PPO plans" and the carrier buttons
  are a "tap your plan → we'll verify it" checker — no carrier is claimed as in-network

## Images
Doctor/team portraits, logo and service photos are the practice's own. The office-gallery has the real team
photo from GBP plus service photos; **no interior office photos were available** — swap in real clinic
photos (GBP has 27) when the client sends them. Hero backdrops and a few panels use free Unsplash images.

## Editing
Edit files in `src/` (CSS, JS, page bodies, shared `blocks/`) and practice facts / FAQs / SEO meta in
`build.py`, then:

```bash
python3 build.py
```

Preview locally (the map embed needs `http://`):

```bash
python3 -m http.server 8000
```
