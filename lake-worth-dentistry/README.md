# Lake Worth Dentistry — Greenacres, FL — "Use It or Lose It" Landing Page

⚠️ **One setup step left before this page shows real ratings/reviews.** The reviews section
(`#reviews`) and the two hero rating badges now pull **live** from the practice's actual Google
Business Profile via the Google Places API — no hardcoded number, no guessing. Until a Places API
key is added, they fail open gracefully (see "Current state" below); nothing is broken or fake, it's
just not live yet.

## Why a live widget instead of a typed-in number

Research turned up a real discrepancy that made publishing a static number unsafe:

- The practice's own site self-reports two different, inconsistent ratings in its own schema.org
  markup: 5.0★/268 reviews in one block, 4.7★/421 in another.
- The only independently-verifiable third-party source found (Yelp, via the exact URL the practice's
  own site links to as its official Yelp page) showed **1.5★ from 6 reviews**, with several substantive
  negative reviews (billing complaints, a patient describing being referred to the Boca Raton office
  mid-root-canal, professionalism complaints).
- Only one clearly positive, attributable review could be verified for this specific location:
  **Sthefany A.** (5★, "I had the best experience going to this dentist!...", truncated on the source
  page).

Rather than guess, publish an unverified number, or hand-copy a screenshot that goes stale the moment
the real rating changes, the page now pulls the rating, review count and top reviews **directly from
Google, live, on every page load** — via `assets/js/gmb-widget.js`. This also means it never needs
editing again as the real rating moves over time.

## Live Google reviews widget — one-time setup (client's own Google account)

The widget code is fully built and wired into the page; it just needs a Places-API-enabled key from
**your own Google Cloud account** to switch on (this can't be a shared/demo key — it must be
restricted to your domain and billed to your account):

1. In [Google Cloud Console](https://console.cloud.google.com/), create/select a project and enable
   the **"Places API"** (not "Places API (New)" unless you also update the code to match — this
   widget uses the classic `PlacesService` JS library).
2. Create an API key under **APIs & Services → Credentials**.
3. **Restrict the key** (Application restrictions → HTTP referrers) to the domain(s) this page will be
   published on, e.g. `https://www.lakeworth-dentistry.com/*`. This stops anyone else from using your
   key/billing if they view-source the page.
4. Open `assets/js/gmb-widget.js` and paste the key into `CONFIG.PLACES_API_KEY` near the top of the
   file (currently `''`).
5. Re-run the bundle command below so the standalone HTML picks up the key too.

**💰 Cost note:** Places API "Place Details" requests that include reviews (Atmosphere Data) are a
**paid** API beyond Google's small monthly free credit. Each page load makes one such request (results
are cached in the visitor's browser for 60 minutes via `sessionStorage` to cut repeat calls). At Google
Ads Display/Performance Max traffic volumes this has a real, ongoing dollar cost — check current
pricing at [mapsplatform.google.com/pricing](https://mapsplatform.google.com/pricing) and consider
setting a daily quota cap on the key in Cloud Console before running paid traffic to this page.

### Current state (no key set yet)

With `CONFIG.PLACES_API_KEY` still empty, the widget fails open cleanly and automatically:
- The two hero rating badges (star+number under the H1, and the "★ Reviews" chip) simply don't render
  — no broken placeholder, no `0.0`.
- The reviews section keeps its heading and shows "See our latest reviews on Google" plus a working
  **Read Reviews on Google** button that links straight to the practice's Google Maps listing — so
  there's always a real, live path to reviews for visitors even before the key is added.
- Once the key is added, all of that is replaced automatically with the real live star rating, review
  count, and the 3 most recent 4★+ written reviews, matching the existing review-card design exactly.

### If you'd rather not manage a Google Cloud key

A no-code alternative is a hosted review-widget service (Elfsight, Trustindex, EmbedSocial, etc.) that
connects to your Google Business Profile and gives you a single embeddable script — happy to swap
`gmb-widget.js` for one of those instead if you provide the embed snippet.

## To finish this page

1. Get a Places-API key from the client's Google Cloud account (see steps above) and drop it into
   `assets/js/gmb-widget.js`.
2. If the client also confirms the site's own review count (268 vs 421) or the Yelp figure is the more
   accurate one, add `aggregateRating` back into the JSON-LD `<script>` block in `<head>` (it was
   intentionally omitted rather than publish a placeholder or unverified number in structured data) —
   or leave it out permanently, since the visible widget is now always accurate without it.
3. Re-render and screenshot-check, then generate the standalone bundle:
   `python3 bundle.py use-it-or-lose-it.html Lake-Worth-Dentistry-Use-It-Or-Lose-It.html`

## Everything else is real and ready

- **Brand colors**: purple `#775FA0` (site's own `btn-tertiary`/CTA color) + charcoal, pulled directly
  from the live site's `dg-colors.css`, not invented.
- **Doctor**: Dr. Naved Fatmi, DMD — same real, verified bio as the Regency Court Dentistry project
  (Florida Board of Dentistry Chairman). Note: research found it's ambiguous whether Fatmi personally
  treats patients at this specific Greenacres location day-to-day, or whether it's primarily run by
  associate dentists (Dr. Mauricio Antezana is also listed for this location) — the page follows the
  practice's own public-facing framing (Fatmi as the featured doctor) per the task brief, without
  claiming his daily on-site presence.
- **Financing**: CareCredit®, LendingClub and Sunbit — all real, confirmed via direct links on the
  practice's own Patient Information page.
- **Insurance carriers**: not named specifically — the site doesn't list named PPO carriers anywhere in
  its static content, so the page says "most PPO plans" rather than naming carriers that couldn't be
  verified.
- **"Previous" landing page** (`book.dentistgreenacresfl.com/claim-insurance-benefits/`): unlike the
  Regency Court project, this one genuinely is real "use it or lose it" content (correct address,
  correct doctor name) — but carries real template-leftover bugs that were NOT reused: a meta
  description for an unrelated practice ("Expressions Dental Care – Dr. John Han"), a stray Texas-area-
  code phone number buried in one CTA, a testimonial naming a different dentist ("Dr. Ortiz"), and a
  stale year (2025).

Phone number used on this page: **(561) 771-6540** (`tel:+15617716540`).
Book online link: **https://book.allinone.dental/lake-worth-dentistry?referrer_id=3**

## Files

```
use-it-or-lose-it.html                              the landing page (production source)
Lake-Worth-Dentistry-Use-It-Or-Lose-It.html          standalone downloadable bundle (single file)
assets/css/theme.css                                 brand tokens + all components (purple/charcoal palette)
assets/js/lp.js                                       countdown, scroll-reveal, animated counters, hours logic, tracking
assets/js/gmb-widget.js                               live Google rating/reviews widget — needs a Places API key, see above
assets/img/                                           real practice photography + logo
bundle.py                                             regenerates the standalone bundle after any edit
```
