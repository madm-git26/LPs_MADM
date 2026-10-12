# Madison Dental Loft — Midtown Manhattan, NYC — "Use It or Lose It" Landing Page

**Midtown office only:** 30 E 40th St, Room 806, New York, NY 10016, led by Dr. Yohan Kim, DMD.
nycdental.com also hosts a second, separate practice, **Concierge Dental Design** (Downtown,
26 Broadway, Dr. Violet Jang). Nothing from Concierge is on this page: not its doctor, address,
phone, VIVOS/sleep content, booking system, logo, favicon or photos. The site's own favicon,
social image and hero video belong to Concierge, so the page's icon is built from Madison's own
"M" mark instead.

Same structure and standing rules as the earlier pages: no services section, no treatment steps,
no footer links, a short doctor section, a clear insurance section, "USE IT OR LOSE IT" up front,
and about 5.8 screens tall on desktop. There was no previous "Use It or Lose It" page to audit.

## Before running ads: booking conversions aren't being recorded

- **The booking link works.** https://book.allinone.dental/madison-dental-loft?referrer_id=4
  opens the correct Midtown schedule with live openings. It's on every Book button as instructed.
- **The page it sends patients to after booking is missing.** After someone books, All in One
  Dental redirects them to `https://www.nycdental.com/thank-you/`, which returns a **404 (page
  not found)**. Any Google Ads conversion that fires on that thank-you page never records, and the
  patient sees an error right after booking. Either create that page on nycdental.com or change
  the redirect in All in One Dental.
- **Tracking.** The current Midtown service page loads Google Tag Manager `GTM-NJCF4GH9` (Ads
  account AW-970786452, call tracking on (646) 930-9679, and a phone-click conversion). Its
  booking-click trigger only matches `book.modento.io`, the old booking system, so clicks on the
  All in One Dental link aren't counted. This new page doesn't load GTM yet. Tell me whether to add
  GTM-NJCF4GH9 or a different container. `assets/js/lp.js` already sends `click_to_call`,
  `click_book_online` and `click_directions` events to `dataLayer` / `gtag`.

## Rating & reviews

**5.0★ from 475 Google reviews** (466 five-star, 98%), read from the Google listing on
12 Oct 2026. The page prints **"475+"** with an October 2026 date stamp so it stays true as the
count grows. The three reviews are verbatim 5★ Google reviews of the Midtown office from 2026:
Yifan Wu, Katie Kamiya (Dr. Kim, implant) and Vlad Albrecht (Dr. Zhang, Invisalign). Two are
shortened with "…" (nothing reworded). `assets/js/gmb-widget.js` is set up for the Midtown
listing: add a Places API key and the rating, count and reviews update live. Key setup and the
cost note are in the Lake Worth / Town Square READMEs.

**Heads-up for the client:** the listing has an older 3★ review about an insurance-billing mix-up
(2023, refunded) and a 2025 1★ about a treatment dispute. People who click through from an
insurance ad may read the billing one, so the page promises a free insurance check and a written
estimate, not guaranteed coverage amounts.

## Real facts used

- **Brand:** colors come from the Madison Dental Loft branding on nycdental.com: navy-slate
  `#52628C` (buttons, top bar), deep `#3F4C6E`, sky `#D0E3FF` and the site's sky-to-white button
  gradient, slate `#535A66`, charcoal `#222`, cream `#FFF9F0`, plus the four blues of the "M"
  logo (`#A1D7FC`, `#5CADE8`, `#3D96DE`, `#2B6FBB`). Square corners, as on the site. The font is
  **Jost** (headings and buttons), as on the site. The photos are the practice's own: Dr. Kim with
  a patient, the reception, the waiting area and Dr. Kim's Grand Central portrait. The reception
  photo is the same one used as the Google listing's cover photo.
- **Insurance wording** comes from the practice's own patient-info pages:
  - *"Most dental insurance benefits reset every year on December 31st. If you don't use your
    benefits before then, they expire."* This is quoted from the practice's Understanding Dental
    Insurance page and used as the page's core message.
  - In-network PPO carriers shown: **Aetna, Cigna, Delta Dental, Guardian, MetLife,
    UnitedHealthcare, GEHA**, plus "most major PPO plans".
    - The site's in-network logo strip is shared with the Downtown office, so only carriers that
      are clearly confirmed for Midtown are named.
    - Delta Dental is shown without "PPO" because Midtown is listed under Delta Dental
      Premier/Dentegra.
    - Anthem and Empire BCBS are left off.
  - "We do not take HMO or Medicaid plans" and the out-of-network PPO reimbursement line come
    from the practice's FAQ.
  - Free insurance check before each visit, a written treatment plan with itemized fees and
    estimated coverage, and claims filed electronically for the patient.
  - Payment is due at the time of service. Accepted: credit/debit cards, HSA/FSA, cash and
    personal check. Financing: Cherry, CareCredit® and in-house payment plans.
  - In-house membership plan: no yearly maximums or waiting periods, and 15% off in-house
    treatment. No prices are shown because the site doesn't list them.
  - Coverage cards: preventive 80–100% is from the practice's insurance FAQ. Basic (~80%) and
    major (~50%) are labeled **"Typical"** because they're standard PPO plan designs, not this
    office's figures.
- **Doctor:** Dr. Yohan Kim, DMD, owner of the practice. Penn Dental Medicine, where he "ranked
  among the top of his class"; postdoctoral residency at Bellevue Hospital Center; clinical
  instructor at NYU, Bellevue and the Hiossen Implant Company (all from his site bio). NY license
  since 2010; his NPI record ties him to the practice. His bio also says FICOI (Fellow of the
  International Congress of Oral Implantologists), but no independent source confirms it, so the
  page leaves it out. Add it if the practice confirms.
- **Midtown team:** Dr. Jonathan Wu, Dr. Kate Zhang, Dr. Jessica Lee and Dr. Raysa Perez. Between
  them, care is offered in English, Mandarin, Korean, Japanese and French (from their bios). All
  are general dentists, so the page makes no specialist claims.
- **Hours:** Mon–Thu 9am–6pm, Fri 9am–5pm, **select Saturdays 9am–3pm**, Sunday closed.
  Saturdays are open only on some weeks. The booking calendar currently shows Oct 17, Oct 31,
  Nov 14, Dec 5 and Dec 12, so Saturday is shown as "Select Saturdays" and left out of the
  search-engine data. Times are Eastern: the countdown ends at 11:59 pm EST on Dec 31, and
  "open now" uses New York time.
- **Location:** between Park and Madison Avenues, about a 3-minute walk from Grand Central (the
  practice's own wording, checked on the map). The Google listing shows a wheelchair-accessible
  entrance.
- **GMB link:** https://maps.app.goo.gl/cHhyKrijFFcwobVC9 is used on Read Reviews on Google and
  both Get Directions links. The embedded map searches "Madison Dental Loft, 30 E 40th St Rm 806"
  so the pin shows the practice, not a bare street address.

## Phone numbers — please confirm

The page uses only the number you gave: **(646) 930-9679** (`tel:+16469309679`). It matches the
call-tracking number in the current Midtown page's tag setup. Other numbers in circulation:
**(646) 687-7898** on nycdental.com and **(646) 624-0987** on the Google listing. Worth
confirming 930-9679 rings the Midtown front desk.

## Not used, on purpose

- Anything from Concierge Dental Design / Downtown: Dr. Violet Jang, 26 Broadway,
  (212) 370-0101, VIVOS, its booking system, its logo, favicon, group photos, or the hero video
  (which shows Dr. Jang).
- Claims the site doesn't support for Midtown: "early morning/evening hours", walk-ins,
  "award-winning", specialist titles, "no surprise bills".
- Generic template lines used on some earlier pages: "4 in 10 Americans…", "reset to $0 on
  January 1st", "no rollover", "2 checkups a year". The page uses the practice's own Dec 31
  wording instead.
- A testimonial on the site that names a "Dr. Sahiba", who isn't on the Midtown team.

## Files

```
use-it-or-lose-it.html                                the landing page (production source)
Madison-Dental-Loft-Midtown-Use-It-Or-Lose-It.html    standalone downloadable bundle
assets/css/theme.css                                  Madison brand tokens + all components
assets/js/lp.js                                       countdown (Eastern time), reveal, hours, tracking
assets/js/gmb-widget.js                               live Google rating/reviews upgrade — optional
assets/img/                                           hero, doctor, reception, background bands, logo, icons
bundle.py                                             regenerates the standalone bundle after any edit
```

Phone: **(646) 930-9679** (`tel:+16469309679`) · Book Online:
**https://book.allinone.dental/madison-dental-loft?referrer_id=4**

Regenerate the bundle after edits:
`python3 bundle.py use-it-or-lose-it.html Madison-Dental-Loft-Midtown-Use-It-Or-Lose-It.html`
