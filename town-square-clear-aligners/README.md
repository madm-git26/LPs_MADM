# Town Square Dentistry (Boynton Beach) — Clear Aligners Landing Page

`clear-aligners.html` — a rebuild of the live page **https://book.boyntontownsquaredentist.com/clear-aligners/**:

- **Structure & components** follow the attached `RegencyInvisalign_final.html` (announcement bar, sticky header,
  hero with Google rating bar + offer flag + hero badge, trust strip, offer panel, card grids, numbered process,
  comparison table, pricing/insurance, doctor feature, auto-scrolling gallery with lightbox, review rail, map +
  hours, FAQ, final CTA, footer, sticky mobile dock, `?kw=` message match, open-now status).
- **Content & images** are the live page's: $1500 off / $4499 Ortho FX / $188 per month offer and fine print,
  free consultation, oral wellness scan and X-rays, "Why choose", issues GIFs, consultation steps and icons,
  health benefits, Dr. Fatmi's bio and photo, the 9 FAQs and the live page's hours.
- **Theme** is the Town Square new-patient page's: teal `#3F9CBB` / `#2E8DAD` / `#2B7690` on charcoal `#252525`,
  light teal `#7CC6DE` accents on dark, Playfair Display + Raleway.

## Setup
- Phone `(561) 564-0026` (`tel:+15615640026`) everywhere; booking `https://book.allinone.dental/town-square-dentistry?referrer_id=1`
- **GTM `GTM-MJHBN9L`** in `<head>` + noscript after `<body>`; robots `noindex, follow`
- Title (58): *Clear Aligners Boynton Beach, FL | $1500 Off | Town Square*; description (153) has no phone number
- dataLayer events match the other Town Square page: `click_to_call`, `click_book_online`, `click_directions`,
  plus `reviews_click`, `message_match`, `scroll_depth` (each with `cta_location`)
- **Message match:** add `?kw=` to ad final URLs to swap the H1 — e.g. `?kw=invisalign`, `?kw=orthofx`,
  `?kw=clear-aligners-cost`, `?kw=teeth-straightening` (full list in `KW_MAP` in `src/app.js`); `{keyword}` in
  `?utm_term=` also works
- Keep the existing URL (`/clear-aligners/`) when you replace the live page so ad final URLs don't change

## Differences from the template, on purpose
- Reviews are Town Square's real 5★ Google reviews (4.7★ / 520) shown statically — the template's live Trustindex
  feed is Regency's account, so it was removed. The template's DearDoc chatbot (Regency's account) was removed too.
- Sections the live page had no content for (comparison, pricing/insurance, reviews, map) are filled only with the
  live page's own statements (its FAQ answers, offer and fine print) and verified Town Square facts.
- Hours are the live page's: Mon 8 am–7 pm, Tue–Fri 8 am–5 pm, Sat & Sun closed.

## Edits made to the live content
- FAQ "How long does Invisalign® treatment usually take?" credited "Dr. Alessandra Coelho", who is not at this
  practice; that clause was removed. Everything else is verbatim.
- The live page contradicts itself (wear time 12 h vs 20–22 h vs 24 h; 6–18 vs 6–11 months). Left as published —
  needs the practice's decision.

## Editing
Edit `src/body.html`, `src/style.css`, `src/app.js` or `build.py`, then `python3 build.py`.
