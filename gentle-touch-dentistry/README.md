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

## Emergency Dentist page

| Page | File |
|---|---|
| Emergency Dentist | `emergency-dentist.html` (generated) |

`emergency-dentist.html` is built by `build_emergency.py` from `general-new-patient.html`: it reuses the
general page's CSS, icons, script and shared sections (credentials, doctors, reviews, gallery, insurance,
contact) and adds the emergency-only sections (conditions, emergency treatments, first aid + ER warning,
5-step emergency visit, emergency FAQ + FAQ schema). Calls are the primary CTA everywhere; booking is
secondary. After editing the general page, rebuild with:

```bash
python3 build_emergency.py
```

Emergency copy is taken from the practice's own emergency-care page. The page never claims 24/7 care —
it says same-day appointments "whenever possible" and points life-threatening cases to 911/ER.

## Stock photography

The practice's own photos (doctors, office tour, patient videos, logo) are used wherever possible. The
generic stock images from the old website were replaced with recent photos from Unsplash, all under the
free **Unsplash License** (commercial use allowed, no attribution required — Unsplash+ paid photos were
excluded). They're served from Unsplash's image CDN with `auto=format&w=…&q=80`, so browsers get WebP/AVIF.

| Where | Unsplash photo |
|---|---|
| Hero background before the video loads (both pages) | [Dentist talking to patient in a modern dental office](https://unsplash.com/photos/dentist-talking-to-patient-in-a-modern-dental-office-Bg81yWKZlMg) |
| General · Cleanings tab | [Dentist examining a man's teeth](https://unsplash.com/photos/dentist-examining-teeth-in-dental-office-BiknMFl7iOw) |
| General · Family tab | [A happy family of three on a couch](https://unsplash.com/photos/a-happy-family-of-three-sitting-on-a-couch-tdkQ_CLYtCc) |
| General · Cosmetic tab | [Close-up of a smiling mouth](https://unsplash.com/photos/close-up-of-a-womans-smiling-mouth-with-red-lipstick-KzmhiJJ041M) |
| General · Emergency tab | [Woman holding a cold compress](https://unsplash.com/photos/woman-in-black-tank-top-holding-white-textile-NKTJCOHzrUM) |
| Both · Insurance card | [Dentist consulting a patient](https://unsplash.com/photos/a-man-smiling-at-another-man-t5o3tjnaFMk) |
| Emergency · Toothache tab | [Person with tooth pain](https://unsplash.com/photos/woman-in-black-framed-eyeglasses-and-black-long-sleeve-shirt-2QOMia2irCU) |
| Emergency · Broken teeth tab | [Dentist showing a damaged tooth model](https://unsplash.com/photos/dentist-showing-a-model-of-a-damaged-tooth-SU6EGDd-ySQ) |
| Emergency · Extraction tab | [Panoramic dental X-ray showing teeth and jawbone](https://unsplash.com/photos/panoramic-dental-x-ray-showing-teeth-and-jawbone-QWgq6Rjw0SE) |
