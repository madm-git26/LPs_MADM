# Belmont Dentistry Peoria — Google Ads Landing Pages

These pages use the same design as the Scottsdale pages (`../belmont-dentistry-scottsdale/`): the same Belmont
brand colours and fonts, the same section layout, and the same centred, compact mobile version. **Peoria office
only:** 7966 W Thunderbird Rd, Suite 101, Peoria, AZ 85381.

| Page | File | Replaces |
|---|---|---|
| New Patient / General Dentist | `new-patients-peoria.html` | belmontdentistry.com/peoria-az/lp/my-new-patients/ |
| Emergency Dentist | `emergency-dentist-peoria.html` | belmontdentistry.com/peoria-az/lp/emergency-dentist/ |
| Thank-you page (shared by both) | `thank-you-peoria.html` | New. Send patients here after they book. |
| Single-file copies | `standalone/*.html` | CSS, JS and every image are built into the file. |

Upload the pages and their `assets/` folder together (fastest). If you use the standalone files, the hero shows the
clinic photo instead of the video until the 6 small files in `assets/video/` are uploaded. After uploading them,
set `VIDEO_BASE_STANDALONE` in `build.py` to their URL and rebuild.

## Links & numbers used on every button

- **Phone:** (623) 887-6008, the Google Ads / CTM tracking number (`tel:+16238876008`). It appears on every call button: 22 call links on the new-patient page and 41 on the emergency page.
- **Book Online:** https://book.allinone.dental/belmont-peoria?referrer_id=4
- **Google Business Profile:** https://maps.app.goo.gl/bR6qu6HvgyW5XJrz5. Used for the rating badges, "Read all reviews" and Get Directions.
- **Map:** the same Belmont Dentistry Peoria Google Maps embed the main site uses.
- **Google Tag Manager:** **GTM-PKC6XXJ** is on all three pages and the standalone copies.
- **Canonical tags:** they point to the existing Peoria landing-page URLs listed above.
- **No forms, no social links.**

The Peoria page of the main website shows (623) 842-1200. These pages use only the tracking number. Two other
things keep calls on the tracking number:

- I removed the entrance-door photo from the page, because the door shows (623) 842-1200.
- The new-patient hero video starts just after that door appears in the clinic's film.

## Content specific to Peoria

All of the following comes from belmontdentistry.com/peoria-az/ and the two current Peoria landing pages.

- **Dentists:** Dr. Puneet Sandhu, DDS (UCLA) and Dr. Jenneth Powell (Midwestern University, Glendale AZ). These are the two dentists the Peoria page lists.
- **Rating:** 4.8★ from **426** Google reviews, read from the site's Peoria review feed in October 2026. Update `RATING` / `REVIEW_COUNT` in `build.py` from time to time.
- **Reviews:** 11 verbatim Google reviews of the Peoria office, spelling included. The emergency page leads with Joe Maus's emergency-extraction review: "worked me into the schedule quickly… a rather painless experience".
- **Photos & video:** the Peoria office's own office-tour photos and its `Peoria.mp4` film.
  - I didn't use the older "office-tour" photos on that page. Their interiors don't match the current office and look like they're from the previous practice.
- **Awards:** Spear Faculty Club (Dr. Sandhu), plus "Patient's Choice 2023" and "Super Practice". The last two come from the current Peoria landing pages.

## Please confirm before running ads

1. **Office hours.**
   - The pages use the hours on the main site's Peoria page:
     - Tue–Thu 7:30 am–5 pm
     - Mon 7:30 am–5 pm and Fri 7:30 am–3 pm, on alternate weeks
     - Closed Saturday and Sunday
   - The current Peoria landing pages list different hours (7 am starts, 6 pm closes and alternate Saturdays). Those look copied from Scottsdale.
   - Tell me which hours are correct. They are in `HOURS` in `build.py` and `assets/js/lp.js`.
   - The live "open now" status runs on Arizona time and tells visitors to call to confirm on Mondays and Fridays.
2. **"Faces Orthodontics Peoria."** I did **not** put this keyword in the page text. Faces Orthodontics is another practice's brand name, and using it in your page copy risks a trademark complaint and misleads patients. The page covers the same search intent with Invisalign / orthodontic treatment in Peoria. If you bid on that keyword, the ad text needs to follow Google's trademark rules too.
3. **"Dentist open today / open now" keywords.** The copy matches these searches, but it only promises what is true: the live open/closed status and "call for the earliest opening". It never claims the office is open when it isn't.
4. **Same-day emergency wording.** The Peoria site says the office "makes every effort" to see emergencies the same day. The pages use that phrasing rather than Scottsdale's "we reserve time every day".
5. **Belmont Dental Plan.** No Peoria price is published, so the pages show the plan's benefits without a price.
6. **Free parking:** stated on the Peoria page of the main site.

## Keywords (Quality Score)

- **New patients:**
  - **Title:** "Dentist in Peoria, AZ | Family Dentist Near You"
  - **H1:** "Peoria's Family Dentist. Never Rushed, Never Judged."
  - **Phrases in the copy:**
    - best dentist in Peoria, AZ
    - Peoria dentists
    - dentist in Peoria
    - family dentist Peoria
    - family dentists near me
    - dentist open today
    - dentists that are open near you
    - dentist near your location
    - local dentist in your area
    - local dentist office
    - Glendale (several times)
- **Emergency:**
  - **Title:** "Emergency Dentist Peoria, AZ | Same-Day Emergency Dental Care"
  - **H1:** "Emergency Dentist in Peoria. Fast Pain Relief."
  - **Phrases in the copy:**
    - emergency dentist near me
    - emergency dentist near me open now
    - emergency dental care
    - emergency dental clinic
    - emergency dental services
    - emergency tooth extraction (11×)
    - emergency extraction
    - Peoria emergency dentist
    - emergency dentist in Peoria

## Thank-you page tracking

`thank-you-peoria.html` sends a `thank_you_view` event to `dataLayer` before GTM loads. The event includes
`lp_source` (`emergency`, `new-patients` or `direct`), which comes from `?from=` in the URL or the referring page.

**Setup:**

1. Publish the page, e.g. at `/peoria-az/lp/thank-you/`.
2. In All-in-One Dental, set the Peoria booking widget's after-booking redirect to that URL.
3. In GTM, create a Custom Event trigger on `thank_you_view` and fire the booking conversion on it.

The landing pages also send `click_to_call`, `click_book_online` and `click_directions` events.

## Editing

All copy lives in `build.py` (Python 3.12+). Edit it, then run:

```bash
python3 build.py
```

That rebuilds all three pages and the standalone copies. `assets/css/belmont.css` and `assets/js/lp.js` are copies
of the Scottsdale files, with the Peoria hours added to the JS.
