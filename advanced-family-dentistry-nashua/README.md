# Advanced Family Dentistry — Nashua, NH — "Use It or Lose It" Landing Page

Ready to run traffic. Built fresh from real, verified content — nothing here is guessed or
invented.

## Rating & reviews — dynamic, with real (modest but genuine) data

This practice doesn't have a huge review volume, but what's there is consistently excellent and
independently confirmed: **Healthgrades shows 5.0★**, **WebMD shows 5.0★ from 10 reviews**, and
Yelp indexes 15 reviews for the location. The practice's own site makes no numeric review claim at
all — just an unnumbered "5 Stars" badge. One third-party SEO aggregator claimed "907" then "932"
reviews on two fetches minutes apart — a clear sign of fabricated/miscalculated content, so that
number is **not used anywhere on this page**. Similarly, the *old* landing page's own schema.org
markup claimed 4.8★/678 reviews, a number no independent source corroborates — also not reused.

This page shows a conservative, fully defensible **5.0★ / 10+ reviews** immediately — no loading
skeleton, no placeholder — plus three real, name-attributed reviews pulled directly from the
practice's own "Read Our Reviews" page. `assets/js/gmb-widget.js` (the same live Google-Places-API
pattern built for the last several projects) is wired in and ready: add your own Places API key and
the rating, review count, and review cards will silently upgrade to **live, real-time data** on
every page load. Without a key, the page simply keeps showing the verified numbers above.

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

- **Brand colors**: royal blue `#0016B7` (the site's own most-used global button color) + gold
  `#F7C800` (the site's own button-hover color) — both confirmed two ways: found directly in the
  live site's CSS, *and* independently confirmed by sampling the actual pixel colors in the
  practice's logo file, so this is genuinely their brand identity, not a guess.
- **Fonts**: Open Sans (body), Libre Baskerville (headings), and Allura (the cursive script accent
  above "Dr. Praveena Bhat" — matches the real site's own decorative-script treatment before section
  headlines). All three are real Google Fonts the site actually loads, so this page pulls them the
  same way, from the Google Fonts CDN.
- **Doctor**: Dr. Praveena Bhat, DMD — confirmed independently by two separate research passes
  against the practice's own `/about/` and `/meet-our-dentists-team-in-nashua/` pages. Real Tufts
  School of Dental Medicine (Advanced Standing Program) training, real professional affiliations
  (ADA, Academy of General Dentistry, NH Dental Society, Greater Nashua Dental Society), and her
  real volunteer work providing dental care to veterans.
  - **Bug caught and NOT used**: the practice's site also has a leaked bio for a **"Dr. Benjamin
    Bunt, DDS"** of "Van, TX" injected into several pages (About, Insurance, Financial Options), plus
    stray "in Van, TX" text under page headlines — clearly leftover boilerplate from a shared
    multi-location website template ("Advanced Family Dentistry" is a reused brand name across many
    unrelated practices nationwide). He has zero real connection to the Nashua office and is not
    featured anywhere on this page.
- **Phone number**: **(603) 836-9898** — the number you provided, and also the number that's already
  correctly used ~10 times throughout the *existing* claim-insurance-benefits page. Flagging for
  awareness: the main site itself (familydentistnashua.com) actually shows **three different**
  numbers depending on the page — (603) 882-3885 in the header/footer, +1 603-821-9046 in its
  schema.org data, and 603-595-2833 on the contact page — none of which match (603) 836-9898. This
  page uses only the number you gave me, consistently, throughout.
- **Insurance carriers**: the site names exactly four — **Delta Dental, Blue Cross Blue Shield, GEHA
  Dental, Guardian Dental** — confirmed via the site's own "Insurance" nav submenu, present on every
  page. No generic "most PPO plans" language was found, so these four are shown as the real plan tags.
- **Financing**: **Cherry** ("Treat Now, Pay Later," 3/6/12/18/24-month plans) is the only named
  third-party financing partner — not CareCredit, not Sunbit, not LendingClub. The practice also
  offers a real in-house **Dental Savings Plan** (membership-style, no yearly maximums/deductibles/
  waiting periods) for uninsured patients — mentioned on this page as a genuine option, not invented.
- **Hours**: Monday–Thursday 8am–5pm, **Friday/Saturday/Sunday closed** — confirmed by two
  independent research passes against both the old landing page and the main site's /contact-us/
  page, which agree exactly.
- **Address**: 537 Amherst St, Nashua, NH 03063 — consistent everywhere it appears.
- **Images**: real logo (full-color, transparent background, shows cleanly on white — no background
  chip needed this time), a real office photo for the hero, and Dr. Bhat's actual headshot from the
  practice's own site.

## Bugs found in the existing landing page — not carried over

The current live LP (`familydentistnashua.com/lp/claim-insurance-benefits/`) has several real,
verified bugs:
- Its hero headline reads **"DENTAL BENEFITS OF 2025"** — stale by a year, and inconsistent with its
  own footer, which correctly says "© 2026."
- A phone-icon button in the header links to **`tel:6038823885`** — a different, wrong number.
- The page's own invisible schema.org data feeds search engines yet a **third** wrong number,
  **603-821-9046** — arguably worse since it's what Google actually reads for rich results.
- A mobile-only "Call to Book" button is broken — its `href` is literally the text
  `<!-- Shortcode [lp_phonenumber_link] does not exist -->`, a failed template shortcode saved as
  the link itself.
- Two different, contradictory, unsourced urgency stats appear in two sections making the same
  claim ("74%" in one, "42%" in another) — neither is reused.
- No real `<meta name="description">` exists; the auto-generated Open Graph description is a broken
  excerpt containing literal leftover HTML markup ("...Read More</a>").

None of this was reused. This page ships with current-year copy, one consistent phone number
everywhere (including in its structured data), a working booking link on every CTA, and real,
written meta tags.

## Files

```
use-it-or-lose-it.html                                      the landing page (production source)
Advanced-Family-Dentistry-Nashua-Use-It-Or-Lose-It.html      standalone downloadable bundle (single file)
assets/css/theme.css                                          brand tokens + all components (royal blue/gold palette)
assets/js/lp.js                                                countdown, scroll-reveal, animated counters, hours logic, tracking
assets/js/gmb-widget.js                                        live Google rating/reviews upgrade — optional, see above
assets/img/                                                    real practice photography, doctor photo, and logo
bundle.py                                                       regenerates the standalone bundle after any edit
```

Phone number used on this page: **(603) 836-9898** (`tel:+16038369898`).
Book online link: **https://book.modento.io/c/d96082ec49b74217b37b8c3547851419/book-website?from_widget=9a117b79b58b472685eafe47d0a7ee6e**
