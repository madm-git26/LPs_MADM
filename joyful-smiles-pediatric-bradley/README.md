# Joyful Smiles Pediatric Dentistry of Bradley — Bradley, IL — "Use It or Lose It" Landing Page

**A separate practice from Joyful Smiles of Tinley Park.** Same owner (Dr. Yaa McDonald), but its own
website (joyfulsmilespediatricdentistry.com), address, phone, Google listing, reviews and visual
brand. Every fact on this page was researched from the Bradley site and the Bradley Google listing;
nothing was copied from the Tinley Park project. Same structure and standing rules as the earlier
pages (no services section, no treatment steps, no footer links, short doctor section, clear
insurance section, "USE IT OR LOSE IT" up front, under 5–6 folds). No previous LP existed to audit.

## Rating & reviews — the Bradley listing's own numbers

**4.9★ from 1,173 Google reviews** (checked 5 Oct 2026), read directly from Google's data for the
Bradley listing (place ID `ChIJI-mrKG_nDYgRU_tkTjLr9QA`, a different listing from Tinley Park) and
matched by the Trustindex widget on the Bradley site, which points at the same place ID. The page
prints "1,170+" so it stays true as the count rises. The site's own homepage badge says "5.0" and its
schema says 1,168 — both stale; not reused. Birdeye's "4.8 / 1,082" is actually the Tinley profile.

Three verbatim 5★ Bradley parent reviews from 2026: Kellie, Lex, Elijah Mayes. `gmb-widget.js` is
wired to the Bradley listing for a live upgrade once a Places API key is added (setup and cost notes
are in the Lake Worth / Town Square READMEs).

**Heads-up for the client:** the Bradley listing has two recent 1★ reviews (a billing/collections
complaint and a papoose-restraint dispute). Ad clicks that check Google will see them; worth replying.

## Real facts used

- **Brand (from the Bradley site's own CSS — different from Tinley Park's):** purple `#612B7D`
  (confirmed in the logo pixels), teal `#12AEAB` / `#1CB1AF`, the yellow-orange "Book Now" gradient
  `#F2C74C → #F29B4A`, the pink-magenta call-button gradient `#EF5E79 → #B64691`, the teal-to-violet
  top bar `#1CB1AF → #6649A6`, and the dark teal-to-purple band `#006B65 → #4C1E5B`. Fonts: Amatic SC
  (headings) and Lato (body), as on the Bradley site. Amatic's loose digits made "4.9" read as
  "4 . 9", so the rating number uses Lato Black instead.
- **Doctor:** Dr. Yaa McDonald, DMD, MDS — shown as practicing at Bradley (Bradley homepage: "Dr
  McDonald and her entire team are looking forward to seeing you at the Bradley office"; a Sept 2026
  post on the Bradley Google listing names her). Same verified credentials as on the Tinley page; the
  unverified board-certification claim is again left out.
  - Not used: the "formerly Fredric Tatel and Associates… since 2017" history on the Bradley site.
    That is Tinley Park's history; the Bradley office opened in August 2018, so the page says
    "since 2018."
  - Not used: "pediatric specialists" for the whole team. Dr. Sara Day, the dentist most clearly
    based at Bradley (her NPI record lists this address), is a general dentist, so the page credits
    pediatric training only to Dr. McDonald.
- **Insurance:** "We accept all major PPO insurance plans" (the site's own wording). The Bradley site
  names no specific carriers, so none are listed. It says in three places that it does **not** accept
  HMO, DMO, Medicaid, Public Aid or All Kids plans; the page says so plainly.
- **Bradley-only offers, from /locations/bradley/:** a free sonic toothbrush with a new-patient exam,
  cleaning and fluoride; a free consultation for uninsured patients when other services are received;
  general anesthesia available in the Bradley office. **Please confirm these are still current** —
  they're on the live site but undated.
- **Financing/payment:** CareCredit; cash, check, Visa, MasterCard, AMEX, Discover.
- **Hours:** Monday–Friday 9am–5pm, closed weekends (site and Google agree). Central time.
- **Address:** 840 N Kinzie Ave, **Suite E**, Bradley, IL 60915. Another dental office (Allcare) is in
  Suite B of the same building, so "Suite E" is shown everywhere and the location card includes the
  real photo of the Bradley sign.
- **GMB link:** https://maps.app.goo.gl/jh4pTFerg4rVS3Xe8 — resolves to "Joyful Smiles Pediatric
  Dentistry Of Bradley". Used on Read Reviews and both Get Directions links; the embedded map searches
  by business name + address.
- **Booking:** https://www.joyfulsmilespediatricdentistry.com/book-now/ is a **working** Typeform
  (unlike the Tinley Park book-now page). It's shared by both locations — it asks "Tinley Park or
  Bradley?" and redirects to kidsdds.net (the Tinley site) after submitting.

## Phone numbers — please confirm

This page uses the number you gave, **(815) 401-9535**. On the Bradley site that number is the
"Emergency Call" line and the number in its search-engine data, and it's on Dr. Day's NPI record. But
the site's header shows **(815) 412-4997**, and Google's listing shows **(815) 934-8606**. Worth
confirming 401-9535 rings the Bradley front desk during office hours.

## Leftovers on the Bradley site worth flagging to the client

- The Bradley contact page says "Consult with our expert dentists for free **at Tinley Park**."
- Tinley Park's "Fredric Tatel" history is in the Bradley site's About page, its schema, and the
  Bradley Google Business Profile description.
- Dr. McDonald's Bradley bio says she's on staff at Children's Hospital of Milwaukee, WI (stale).
- One "review" on the Bradley site (Jessica Billingsley) is actually the practice's own reply text.
- Several gallery photos are of a Tinley Park event booth (old 16345 S. Harlem address).

## Files

```
use-it-or-lose-it.html                                     the landing page (production source)
Joyful-Smiles-Pediatric-Dentistry-Bradley-Use-It-Or-Lose-It.html   standalone downloadable bundle
assets/css/theme.css                                       Bradley brand tokens + all components
assets/js/lp.js                                            countdown (Central time), reveal, hours, tracking
assets/js/gmb-widget.js                                    live Google rating/reviews upgrade — optional
assets/img/                                                hero, doctor, Bradley office photo, logo, kid cut-out
bundle.py                                                  regenerates the standalone bundle after any edit
```

Phone: **(815) 401-9535** (`tel:+18154019535`) · Request Appointment:
**https://www.joyfulsmilespediatricdentistry.com/book-now/**
