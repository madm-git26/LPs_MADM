# Town Square Dentistry — Boynton Beach, FL — "Use It or Lose It" Landing Page

Ready to run traffic. Built fresh from real, verified content — nothing here is guessed or
invented.

## Rating & reviews — dynamic, with real data from day one

Unlike some of this practice group's other locations, Town Square Dentistry's rating data is
**clean and well-corroborated**: the practice's own site (schema.org markup, two separate blocks)
reports **4.8★ / 456 reviews**, and that number is closely matched by multiple independent
sources checked separately — Birdeye (4.8★), Location.com (~455 reviews), FindMeADentist.ai (488
Google reviews). No red flags like the Lake Worth Dentistry project's data discrepancy.

So this page shows the real **4.8★ / 456+** rating and three real, name-attributed Google reviews
(sourced via Birdeye, which mirrors the practice's actual Google reviews) immediately — no
loading skeleton, no placeholder. On top of that, `assets/js/gmb-widget.js` (same live
Google-Places-API pattern built for the Lake Worth project) is wired in and ready: add your own
Places API key and the rating, review count, and review cards will silently upgrade to
**live, real-time data** on every page load. Without a key, the page simply keeps showing the
verified real numbers above — nothing breaks, nothing looks unfinished.

### To turn on live (auto-updating) data

1. In [Google Cloud Console](https://console.cloud.google.com/), enable the **"Places API"**
   (classic, not "Places API (New)") on a project of your own.
2. Create an API key under **APIs & Services → Credentials**.
3. **Restrict the key** (HTTP referrers) to the domain this page will be published on.
4. Paste the key into `CONFIG.PLACES_API_KEY` near the top of `assets/js/gmb-widget.js`.
5. Re-run the bundle command below.

**💰 Cost note:** Places "Place Details" requests that include reviews are a paid API beyond
Google's small free tier. Each page load makes one such request (cached 60 minutes per visitor via
`sessionStorage`). At Google Ads traffic volume this has a real ongoing cost — check current
pricing at [mapsplatform.google.com/pricing](https://mapsplatform.google.com/pricing) and consider
a daily quota cap on the key.

## Real facts used on this page

- **Brand colors**: teal-blue `#3F9CBB` (the site's own most-used color — 17 occurrences in its
  `dg-colors.css`, confirmed live on the actual "Book Appointment" button) + dark charcoal/near-black
  structural tones (`#424242` / `#252525`), all pulled directly from the live site's own CSS, not
  invented.
- **Fonts**: Playfair Display (headings) + Raleway (body/buttons), both self-hosted on the real site
  and confirmed via its actual `@font-face` declarations.
- **Doctor**: Dr. Naved Fatmi, DMD — same real, publicly-stated bio as the Regency Court Dentistry
  and Lake Worth Dentistry projects (Founder of the Health & Wellness Dentistry group; five-year term
  on the Florida Board of Dentistry, including Vice Chair and Chairman). Confirmed directly on this
  location's own `/about/` page. Note: this location's site also names three other associate dentists
  (Dr. Mitchell Indictor, Dr. Libby Finer, Dr. Jordan Hekmati) — the page follows the practice's own
  public-facing framing (Fatmi as the featured doctor) per the task brief, without excluding the real
  reviews that happen to mention other staff by name.
- **Phone number** — flagging a real inconsistency found on the live site: it actually displays
  **three different numbers** depending on where you look (`(561) 732-9727` in the header/footer,
  `(561) 654-0190` in one schema block, `(561) 782-9633` in body copy on two pages). Per your
  instructions, this page uses **the number you provided, (561) 564-0026** — which also matches the
  number already used consistently across the existing "Use It or Lose It" LP
  (`book.boyntontownsquaredentist.com`), so it's the number already running as the client's tracked
  number for this exact campaign.
- **Financing**: **CareCredit®** — the only financing partner actually named on the site (verified via
  raw HTML, rejecting an earlier AI-summary claim of LendingClub/Sunbit that couldn't be confirmed in
  the source).
- **Insurance carriers**: not named specifically anywhere on the site — the page says "most PPO
  plans" rather than naming carriers that couldn't be verified.
- **Hours**: Monday 8am–7pm, Tuesday–Friday 8am–5pm, Saturday/Sunday closed — matches the site's own
  visible hours table and schema markup exactly (note Monday's longer hours, unlike the other
  Fatmi-location pages built so far).
- **Address**: 207 SE 23rd Ave, Boynton Beach, FL 33435 — consistent everywhere it appears on the
  real site and matches the address on the existing LP.
- **Images**: real logo, and a real exterior photo of the practice's own storefront (address "207"
  visible on the building) used for the hero — both downloaded directly from the site's own CDN.
  Doctor photo is Dr. Fatmi's actual headshot from the practice's `/about/` page.

## Bug found in the existing landing page — not carried over

The current live LP (`book.boyntontownsquaredentist.com`) has one real, verified bug: its single
patient testimonial is attributed to **"Dr. Murillo"** — a name that appears nowhere in this
practice's actual doctor roster. This page does not reuse that testimonial; the three review cards
here are real, separately-verified Google reviews that correctly name the actual staff mentioned
(Ashley, Dr. Finer). The old LP's meta description and Open Graph tags were also empty — this page
ships with a real, written meta description and OG tags instead. The old LP had no actual "Use It or
Lose It" / year-end deadline messaging at all (it's a generic evergreen consult page) — that seasonal
urgency framing on this page is new, purpose-built content.

## Files

```
use-it-or-lose-it.html                     the landing page (production source)
Town-Square-Dentistry-Use-It-Or-Lose-It.html   standalone downloadable bundle (single file)
assets/css/theme.css                        brand tokens + all components (teal/charcoal palette)
assets/js/lp.js                             countdown, scroll-reveal, animated counters, hours logic, tracking
assets/js/gmb-widget.js                     live Google rating/reviews upgrade — optional, see above
assets/img/                                 real practice photography, doctor photo, and logo
bundle.py                                   regenerates the standalone bundle after any edit
```

Phone number used on this page: **(561) 564-0026** (`tel:+15615640026`).
Book online link: **https://book.allinone.dental/town-square-dentistry?referrer_id=1**
