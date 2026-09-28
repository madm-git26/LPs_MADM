# Burton Family Dental — Burton, MI — "Use It or Lose It" Landing Page

Ready to run traffic. Built fresh from real, verified content — nothing here is guessed or
invented.

## Rating & reviews — dynamic, with real data from day one

Rating data here is strong and broadly consistent: the practice's own site self-reports **5.0★ /
681 reviews** (schema.org markup), while an independent pull via Birdeye (itself sourced entirely
from Google) shows **4.9★ / 999 reviews**. Both numbers clearly describe a genuinely excellent,
well-reviewed practice — this is nothing like the Lake Worth Dentistry project's contradiction —
but the exact review count differs by source and by pull date, so rather than quote either exact
figure, this page uses a conservative, defensible **4.9★ / 650+ reviews** (below what every source
actually shows).

The page shows that real rating and three real, name-attributed reviews immediately — no loading
skeleton, no placeholder. `assets/js/gmb-widget.js` (the same live Google-Places-API pattern built
for the Lake Worth and Town Square projects) is wired in and ready: add your own Places API key and
the rating, review count, and review cards will silently upgrade to **live, real-time data** on
every page load. Without a key, the page simply keeps showing the verified real numbers above —
nothing breaks, nothing looks unfinished.

**GMB link**: all map touchpoints (the "Read Reviews on Google" button, both "Get Directions"
links, and the embedded map) use the client-provided link —
**https://maps.app.goo.gl/qR7kKq3oHFJEPjpy5** — which resolves to "Burton Family Dental" at the
correct 5136 Davison Rd address/coordinates. The embedded map's query was also updated to include
the business name (not just the address) so its pin resolves to the actual business listing rather
than a generic street-address marker.

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

- **Brand colors**: navy `#033C72` (the site's own most-used structural color — header bar, many
  section backgrounds) + bright cyan-blue `#0097D3` (confirmed live as the site's actual global
  button color: `.x-btn,.button,[type="submit"]{background-color:#0097D3}`), both pulled directly
  from the live site's own inline CSS, not invented.
- **Fonts — self-hosted, embedded exactly as the real site serves them**: "Lemon Milk" (headings)
  and "Proxima Nova" (body/buttons). Neither font is available on Google Fonts — both are the
  practice's own commercial webfonts, self-hosted from their own CDN. Rather than substitute a
  free look-alike, this page downloads and embeds the actual `.woff` files the real site uses (see
  `assets/fonts/`), so the type genuinely matches the client's brand, not an approximation. This is
  why the bundled file is larger than prior projects (~1.7MB vs. ~0.3–1.7MB) — the font files
  themselves account for most of that.
- **Doctor**: Dr. Chintan Shah, DDS — the sole dentist named on the practice's own site, confirmed
  via its `/about-us/` page and schema.org markup ("founder": "Dr. Chintan Shah"). His stated bio on
  the real site is brief (general/cosmetic dentistry, endodontics, oral surgery, implant surgery,
  patient education) — no dental school or graduation year is published anywhere on the practice's
  own site, so none is claimed here.
- **Phone number**: **(810) 674-3060** — this is the number you provided and the number the live
  site actually displays to visitors on every page. Flagging for awareness: the site's own
  schema.org markup and several third-party directories (BBB, Birdeye, Healthgrades) list a
  different number, (810) 742-6060 — likely the underlying/legal-entity number behind a
  call-tracking line. This page uses (810) 674-3060 throughout, per your instructions.
- **Financing**: **CareCredit®** and **LendingPoint** — both confirmed via real logo images on the
  site's `/finance/` page (note: LendingPoint, not LendingClub — the two are easy to conflate and
  are different companies).
- **Insurance carriers**: the site actually names carriers (unlike some sibling projects), shown as
  logos on `/finance/`: Aetna, Delta Dental, Cigna, Blue Cross Blue Shield, Guardian, MetLife,
  Humana, GEHA, Principal, Ameritas, Assurant, Dearborn National, Lincoln Financial Group, Dental
  Select, AlwaysCare, Great-West Healthcare. Six of the most recognizable are shown as plan tags on
  this page. The real site also explicitly states it does **not** accept Medicaid, HMO, or state
  insurance plans — that caveat is carried over honestly rather than omitted.
- **Hours**: Monday–Thursday 8am–6pm, Friday 9am–1pm (a shorter day — note this differs from every
  other project built so far), Saturday/Sunday closed — matches the real site's hours table exactly.
- **Address**: 5136 Davison Rd, Burton, MI 48509 — consistent everywhere it appears on the real site.
- **Images**: real logo (white artwork, so it's shown on a navy background chip in the header for
  contrast — the mark itself is untouched, only its background was added), a real team photo for the
  hero, and Dr. Shah's actual headshot from the practice's `/about/` page — all downloaded directly
  from the site's own CDN.

## Bugs found in the existing landing page — not carried over

The current live LP (`burtonfamilydentalmi.com/claim-insurance-benefits/`) has several real,
verified bugs:
- Its `<title>` tag reads **"Dental Insurances 2021"** — stale by five years.
- Body copy references benefits "start[ing] fresh in **2022**" — also stale.
- A **"DENTAL BENEFITS OF 2025"** section is duplicated verbatim and is itself now a year out of
  date.
- A stray, wrong-region phone number, **"1-817-984-5419"** (Fort Worth, TX area code), sits directly
  in the "Beat the END OF YEAR RUSH" urgency banner — not the real (810) 674-3060 number.
- The page's `og:title` meta tag is empty (would show blank if shared on social).

None of this was reused. This page ships with a correct 2026 date throughout, a single verified
phone number everywhere, and complete Open Graph tags.

## Files

```
use-it-or-lose-it.html                    the landing page (production source)
Burton-Family-Dental-Use-It-Or-Lose-It.html  standalone downloadable bundle (single file)
assets/css/theme.css                       brand tokens + all components (navy/cyan palette), with the real brand fonts embedded inline
assets/fonts/                              the practice's own self-hosted Lemon Milk + Proxima Nova .woff files
assets/js/lp.js                            countdown, scroll-reveal, animated counters, hours logic, tracking
assets/js/gmb-widget.js                    live Google rating/reviews upgrade — optional, see above
assets/img/                                real practice photography, doctor photo, and logo
bundle.py                                  regenerates the standalone bundle after any edit
```

Phone number used on this page: **(810) 674-3060** (`tel:+18106743060`).
Request Appointment link: **https://www.burtonfamilydentalmi.com/request-an-appointment/**
