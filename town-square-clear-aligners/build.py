#!/usr/bin/env python3
"""
Build the Town Square Dentistry (Boynton Beach) clear-aligner landing page.

    clear-aligners.html   — rebuild of https://book.boyntontownsquaredentist.com/clear-aligners/
                            in the section structure of the Regency Invisalign page,
                            with the live page's content and images, in Town Square's theme.

Sources in src/:  style.css (re-skinned template CSS), app.js (adapted template script),
body.html (page markup with tokens), lightbox.html.   Re-run after editing:

    python3 build.py
"""
import html as htmllib
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")
OUT = "clear-aligners.html"

PHONE = "(561) 564-0026"
TEL = "tel:+15615640026"
BOOK_URL = "https://book.allinone.dental/town-square-dentistry?referrer_id=1"
MAPS = "https://maps.app.goo.gl/hYPqYdSCWkGLrhfM9"
MAP_EMBED = ("https://maps.google.com/maps?q=Town+Square+Dentistry+-+Dentist+Boynton+Beach,"
             "+207+SE+23rd+Ave,+Boynton+Beach,+FL+33435&z=15&output=embed")
GTM_ID = "GTM-MJHBN9L"
RATING, COUNT = "4.7", "520"       # Google Business Profile, Nov 2026
LIVE = "https://d9hhrg4mnvzow.cloudfront.net/book.boyntontownsquaredentist.com/clear-aligners"
TS_SITE = "https://www.boyntonbeachtownsquaredentistry.com/wp-content/themes/naved-dental/assets/media"
TITLE = "Clear Aligners Boynton Beach, FL | $1500 Off | Town Square"
DESC = ("Clear aligners in Boynton Beach, FL — limited-time $1500 off: $4499 OrthoFX aligners or $188/month. "
        "Free consultation, 3D smile scan & X-rays.")


def read(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as f:
        return f.read()


def svg(inner, size=24, sw="1.8"):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{inner}</svg>')


P = {
    "star": '<path d="M12 2 15.09 8.26 22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14l-5-4.87 6.91-1.01L12 2z"/>',
    "cal": '<rect x="3" y="4" width="18" height="18" rx="2.5"/><path d="M16 2v4M8 2v4M3 10h18"/>',
    "calchk": '<rect x="3" y="4" width="18" height="18" rx="2.5"/><path d="M16 2v4M8 2v4M3 10h18M9 16l2 2 4-4"/>',
    "phone": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .3 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.2a2 2 0 0 1 2.1-.5c.9.4 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "x": '<path d="M18 6 6 18M6 6l12 12"/>',
    "tag": '<path d="M20.6 13.4 12 22l-8.6-8.6a5.5 5.5 0 0 1 0-7.8 5.5 5.5 0 0 1 7.8 0l.8.8.8-.8a5.5 5.5 0 0 1 7.8 0 5.5 5.5 0 0 1 0 7.8z"/>',
    "shield": '<path d="M12 2 4 5v6.5c0 4.6 3.4 8.9 8 10.5 4.6-1.6 8-5.9 8-10.5V5l-8-3z"/><path d="m9 12 2 2 4-4"/>',
    "award": '<circle cx="12" cy="8" r="5"/><path d="M8.2 12.5 7 22l5-2.5L17 22l-1.2-9.5"/>',
    "grad": '<path d="M12 3 2 8l10 5 10-5-10-5z"/><path d="M6 10.5V16c0 1.7 2.7 3 6 3s6-1.3 6-3v-5.5"/><path d="M22 8v6"/>',
    "scan": '<rect x="2" y="4" width="20" height="14" rx="2.5"/><path d="M8 21h8M12 18v3"/><path d="M6.5 11.5 9 9l2.5 2.5L14 8l3.5 4.5"/>',
    "xray": '<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M8 8c1.5 1 2.5 1 4 0s2.5-1 4 0M8 12h8M8 16c1.5-1 2.5-1 4 0s2.5 1 4 0"/>',
    "eye": '<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    "smile": '<circle cx="12" cy="12" r="9.5"/><path d="M8 14.5c1 1.3 2.4 2 4 2s3-.7 4-2M9 9.5h.01M15 9.5h.01"/>',
    "hand": '<path d="M12 21s-7.5-4.6-9.3-9A5.3 5.3 0 0 1 12 6.6 5.3 5.3 0 0 1 21.3 12c-1.8 4.4-9.3 9-9.3 9z"/>',
    "clock": '<circle cx="12" cy="12" r="9.5"/><path d="M12 6.5v6l3.5 2"/>',
    "card": '<rect x="2" y="5" width="20" height="14" rx="2.5"/><path d="M2 10h20M6 15h4"/>',
    "dollar": '<path d="M12 2v20M17.5 6.5c0-2-2.5-3-5.5-3s-5.5 1-5.5 3.2c0 4.8 11 2.6 11 7.4 0 2.3-2.5 3.4-5.5 3.4s-5.5-1.1-5.5-3.2"/>',
    "pin": '<path d="M12 21s-7-5.2-7-11a7 7 0 1 1 14 0c0 5.8-7 11-7 11z"/><circle cx="12" cy="10" r="2.6"/>',
    "file": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M9 13h6M9 17h6"/>',
    "pulse": '<path d="M3 12h4l2.5-7 4 14 2.5-7h5"/>',
}
ARCH = ('<svg width="26" height="9" viewBox="0 0 26 9" fill="none" aria-hidden="true"><path d="M1 8C1 4 6 1 13 1s12 3 12 7" '
        'stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/></svg>')
GLOGO = ('<svg class="g" viewBox="0 0 48 48" aria-hidden="true"><path fill="#FFC107" d="M43.6 20.1H42V20H24v8h11.3C33.7 32.7 29.2 36 24 36c-6.6 0-12-5.4-12-12s5.4-12 12-12c3.1 0 5.8 1.2 7.9 3.1l5.7-5.7C34.1 6.1 29.3 4 24 4 12.9 4 4 12.9 4 24s8.9 20 20 20 20-8.9 20-20c0-1.3-.1-2.6-.4-3.9z"/>'
         '<path fill="#FF3D00" d="m6.3 14.7 6.6 4.8C14.7 15.1 19 12 24 12c3.1 0 5.8 1.2 7.9 3.1l5.7-5.7C34.1 6.1 29.3 4 24 4 16.3 4 9.7 8.3 6.3 14.7z"/>'
         '<path fill="#4CAF50" d="M24 44c5.2 0 9.9-2 13.4-5.2l-6.2-5.2C29.2 35.1 26.7 36 24 36c-5.2 0-9.6-3.3-11.3-7.9l-6.5 5C9.5 39.6 16.2 44 24 44z"/>'
         '<path fill="#1976D2" d="M43.6 20.1H42V20H24v8h11.3c-.8 2.2-2.2 4.2-4.1 5.6l6.2 5.2C36.9 40.2 44 35 44 24c0-1.3-.1-2.6-.4-3.9z"/></svg>')

FAQ = [
    ("How do clear aligners work?",
     "Clear aligners are custom-made, transparent trays designed to gradually straighten your teeth. Using advanced 3D imaging technology, your dentist creates a personalized treatment plan that maps out each stage of tooth movement. By wearing a series of aligners, each slightly adjusted, your teeth are gently shifted into their ideal positions. Aligners should be worn 20–22 hours a day and changed every 1–2 weeks for optimal results. Their removable design also makes it easy to eat, brush, and floss normally."),
    ("Are clear aligners better than braces?",
     "Clear aligners offer several advantages over traditional braces, making them a popular choice for many patients. They are virtually invisible, more comfortable, and can be removed for eating and oral hygiene. Aligners also require fewer in-office visits and typically cause less irritation since they lack metal brackets or wires. For mild to moderate misalignments, aligners can be just as effective as braces, often achieving results faster. However, complex cases may still benefit from traditional braces. Consulting with an experienced dentist can help determine the best option for your smile."),
    ("How long does aligner treatment take?",
     "Clear aligner treatment typically takes 6 to 18 months, depending on the complexity of your case and how consistently you wear the aligners. Minor adjustments may be completed in as little as six months, while more significant corrections might take longer. Wearing your aligners for the recommended 20–22 hours daily and following your dentist’s instructions are crucial for achieving timely results. During your free consultation, your dentist will provide a personalized timeline based on your unique smile goals."),
    ("What should I expect after completing my Invisalign® treatment?",
     "Following Invisalign® treatment, our dentists advise wearing a retainer nightly to prevent teeth from shifting back to their original positions. Customized post-treatment care may be recommended based on individual dental needs to maintain your beautiful smile long-term."),
    ("Can Invisalign® correct severe dental issues like overcrowding?",
     "Invisalign® is effective for treating a wide range of dental issues, including mild to moderate overcrowding. Severe cases may require alternative treatments, which our experienced team can discuss during your consultation."),
    ("Are there any dietary restrictions with Invisalign®?",
     "There are no dietary restrictions with Invisalign®. You can eat your food without restrictions."),
    ("How long does Invisalign® treatment usually take?",
     "Invisalign® treatment typically lasts between 6 to 11 months. However, the duration varies based on individual treatment plans and goals."),
    ("What are the key differences between Invisalign® and traditional braces?",
     "Unlike traditional braces, Invisalign® is made from SmartTrack technology for enhanced effectiveness, predictability, and better oral hygiene. Additionally it is virtually invisible. Invisalign® is also made from SmartTrack materials providing an enhanced effectiveness of aligners."),
    ("Do I need to wear my Invisalign® trays all day?",
     "It's recommended to wear Invisalign® trays for 24 hours daily to ensure effective teeth alignment and to maintain the progress of your treatment plan."),
]

REVIEWS = [
    ("Tanya Guez-Nisenson", "I had a really positive experience with the staff here. Everyone was warm, welcoming, helpful, and very accommodating."),
    ("Roya Gandjei", "I recently had my wisdom teeth removed by Dr. Indictor, and I had a really great experience. Dr. Indictor and his assistant, Jessica, were so patient and reassuring that they helped me feel calm the entire time."),
    ("Kimberly Chavez", "Very very professional office, everybody is so sweet, they enjoy their job you can tell."),
]


def schema():
    g = [{
        "@type": ["Dentist", "MedicalBusiness", "LocalBusiness"],
        "@id": "https://www.boyntonbeachtownsquaredentistry.com/#practice",
        "name": "Town Square Dentistry - Dentist Boynton Beach",
        "url": "https://www.boyntonbeachtownsquaredentistry.com/",
        "telephone": "+1-561-564-0026",
        "image": f"{LIVE}/585995fb-invisalign-img1_10000000rs0px05j000000.jpg",
        "priceRange": "$$",
        "address": {"@type": "PostalAddress", "streetAddress": "207 SE 23rd Ave", "addressLocality": "Boynton Beach",
                    "addressRegion": "FL", "postalCode": "33435", "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": 26.5074633, "longitude": -80.0643806},
        "hasMap": MAPS,
        "openingHoursSpecification": [
            {"@type": "OpeningHoursSpecification", "dayOfWeek": "Monday", "opens": "08:00", "closes": "19:00"},
            {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Tuesday", "Wednesday", "Thursday", "Friday"],
             "opens": "08:00", "closes": "17:00"},
        ],
        "employee": {"@type": "Person", "name": "Dr. Naved Fatmi", "jobTitle": "Dentist, D.M.D.",
                     "alumniOf": "University of Florida College of Dentistry"},
        "aggregateRating": {"@type": "AggregateRating", "ratingValue": RATING, "bestRating": "5", "reviewCount": COUNT},
        "review": [{"@type": "Review", "author": {"@type": "Person", "name": n},
                    "reviewRating": {"@type": "Rating", "ratingValue": "5", "bestRating": "5"}, "reviewBody": b}
                   for n, b in REVIEWS],
        "makesOffer": {"@type": "Offer", "name": "Ortho FX clear aligners — limited-time $1500 off",
                       "price": "4499", "priceCurrency": "USD",
                       "description": "$4499 clear aligners or $188 per month. Free consultation, complimentary oral wellness scan and free X-rays."},
    }, {
        "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ],
    }]
    return ('<script type="application/ld+json">\n'
            + json.dumps({"@context": "https://schema.org", "@graph": g}, indent=2, ensure_ascii=False) + "\n</script>")


def faq_html():
    return "\n".join(f'      <details{" open" if i == 0 else ""}>\n        <summary>{q}</summary>\n'
                     f'        <div class="ans"><p>{a}</p></div>\n      </details>' for i, (q, a) in enumerate(FAQ))


def render(text, toks):
    text = re.sub(r"\{\{I:(\w+)(?::(\d+))?(?::([\d.]+))?\}\}",
                  lambda m: svg(P[m.group(1)], int(m.group(2) or 24), m.group(3) or "1.8"), text)
    text = re.sub(r"\{\{([A-Z_0-9]+)\}\}", lambda m: toks.get(m.group(1), m.group(0)), text)
    left = re.findall(r"\{\{[^}]+\}\}", text)
    if left:
        raise SystemExit(f"Unreplaced tokens: {sorted(set(left))}")
    return text


def build():
    assert len(TITLE) <= 60 and len(DESC) <= 160, (len(TITLE), len(DESC))
    with open(os.path.join(SRC, "gbp.json"), encoding="utf-8") as f:
        gbp = json.load(f)
    toks = {
        "PHONE": PHONE, "TEL": TEL, "BOOK": f'href="{BOOK_URL}" target="_blank" rel="noopener"',
        "MAPS": MAPS, "MAPEMBED": MAP_EMBED, "RATING": RATING, "COUNT": COUNT, "LIVE": LIVE, "TS_SITE": TS_SITE,
        "ARCH": ARCH, "GLOGO": GLOGO, "LOGO": read("logo.b64").strip(), "LOGO_WHITE": read("logo-white.b64").strip(),
        "FAQ_ITEMS": faq_html(), "LIGHTBOX": read("lightbox.html"),
        "GBP_WAIT": gbp["wait"], "GBP_EXT": gbp["ext"], "GBP_HYG": gbp["hyg"],
    }
    head = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':
new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
}})(window,document,'script','dataLayer','{GTM_ID}');</script>
<!-- End Google Tag Manager -->
<title>{htmllib.escape(TITLE)}</title>
<meta name="description" content="{htmllib.escape(DESC)}">
<meta name="robots" content="noindex, follow">
<meta name="googlebot" content="noindex, follow">
<meta name="theme-color" content="#252525">
<meta name="format-detection" content="telephone=no">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Town Square Dentistry">
<meta property="og:title" content="{htmllib.escape(TITLE)}">
<meta property="og:description" content="{htmllib.escape(DESC)}">
<meta property="og:image" content="{LIVE}/585995fb-invisalign-img1_10000000rs0px05j000000.jpg">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="{read('favicon.b64').strip()}" type="image/png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preconnect" href="https://d9hhrg4mnvzow.cloudfront.net" crossorigin>
<link rel="preload" as="image" fetchpriority="high" href="{LIVE}/585995fb-invisalign-img1_10000000rs0px05j000000.jpg">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,600;1,700&family=Raleway:wght@400;500;600;700;800&display=swap">
{schema()}
<style>
{read('style.css')}
</style>
</head>
<body>
<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id={GTM_ID}" height="0" width="0" style="display:none;visibility:hidden" title="Google Tag Manager"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->
"""
    body = render(read("body.html"), toks)
    html = head + body + "\n<script>\n" + read("app.js") + "\n</script>\n</body>\n</html>\n"
    with open(os.path.join(HERE, OUT), "w", encoding="utf-8") as f:
        f.write(html)
    print(f"wrote {OUT} ({len(html) / 1024:.0f} KB)")


if __name__ == "__main__":
    build()
