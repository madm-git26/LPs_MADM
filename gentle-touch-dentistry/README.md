# Gentle Touch Dentistry Richardson — Google Ads Landing Pages

| Page | File |
|---|---|
| General / New Patient | `general-new-patient.html` |

- **Ads phone:** (469) 336-3069 → `tel:+14693363069` (the main site lists (469) 947-3963; this page uses the ads number everywhere)
- **Book Online:** `https://book.allinone.dental/gentle?referrer_id=3`
- **GBP:** https://maps.app.goo.gl/3b5hkvUb6ybnhUne9
- Single self-contained HTML file (inline CSS + JS). Images, hero video and patient videos load from
  `mygentletouchdentistry.com`, so the file works anywhere without an assets folder.
- Theme tokens from the live site: brand `#1f4e8c`, ink `#132a4a`, sky `#5bb8e8`, gold `#e7b567`;
  fonts Plus Jakarta Sans (headings), Figtree (body), Fraunces italic (accents).
- Tracking: `click_to_call`, `click_book_online`, `click_directions`, `play_testimonial` are pushed to
  `dataLayer` / `gtag`. Paste the Google Ads ID + labels into `CONFIG` at the top of the page script.
- Ships with `noindex, nofollow` (same as the other LPs in this repo) — remove it if you want it indexed.
- Rating (5.0 / 107 reviews) is hard-coded from the practice website — refresh periodically.
