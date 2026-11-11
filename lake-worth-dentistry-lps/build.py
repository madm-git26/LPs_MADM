#!/usr/bin/env python3
"""
Build the two Lake Worth Dentistry (Greenacres, FL) Google Ads landing pages.

    dentist-lake-worth.html             general / new patient   (slug /dentist-lake-worth/)
    emergency-dentist-lake-worth.html   emergency               (slug /emergency-dentist-lake-worth/)

Each output is ONE self-contained HTML file (inline CSS + JS, logo embedded, photos hot-linked
from the practice's website/CDN, Google Business Profile and Unsplash), so it can be pasted into a
WordPress "Custom HTML" block / blank page template, or uploaded anywhere as-is.

Source lives in src/:
    base.css, emergency.css, app.js, sprite.svg, logo*.b64, favicon.b64
    general.html, emergency.html           page bodies
    blocks/*.html                          sections shared by both pages

Tokens like {{PHONE}} are replaced at build time; {{ICO:name}} becomes an inline
icon; {{INCLUDE:name}} pulls in src/blocks/name.html. Re-run after editing:

    python3 build.py
"""
import html as htmllib
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "src")


def _b64(name):
    with open(os.path.join(SRC, name), encoding="utf-8") as f:
        return f.read().strip()


# ---------------------------------------------------------------- practice facts
PRACTICE = "Lake Worth Dentistry"
PHONE = "(561) 771-6540"           # Google Ads tracking number (main site lists a different one)
TEL = "tel:+15617716540"
BOOK_URL = "https://book.allinone.dental/lake-worth-dentistry?referrer_id=3"
MAPS = "https://maps.app.goo.gl/Pm2TNk8EZXfFy3HU8"
MAP_EMBED = ("https://maps.google.com/maps?q=Lake+Worth+Dentistry,"
             "+6427+Lake+Worth+Rd+Ste+B,+Greenacres,+FL+33463&z=15&output=embed")
GTM_ID = "GTM-5J22NPZS"
RATING = "4.7"
COUNT = "459"                      # Google Business Profile, Nov 2026 — refresh periodically
SITE = "https://www.lakeworth-dentistry.com/wp-content/themes/naved-dental/assets/media"
CF = "https://d11iwgb7g2683x.cloudfront.net/lakeworth-dentistry/wp-content/uploads"
LOGO = _b64("logo.b64")            # the practice's purple logo (no public URL exists), embedded
LOGO_WHITE = _b64("logo-white.b64")
FAVICON = _b64("favicon.b64")
UN = "https://images.unsplash.com/photo-"
# Real office photos from the Google Business Profile
GBP_OP = "https://lh3.googleusercontent.com/grass-cs/AABkmLfjImwy4iQnY1rXxIX1ZFhl6QeBOm_2oXMExvVgYXV0gwmGbZ3cdoab8yMOWkQuyuwhovmEWJecCeey7cjqfPEIZd3gQMftgTJkcBRDzC-gpiRNyqZLgLEB8xL1pA4vLmjA_E52"      # treatment room with chairside screen
GBP_IN = "https://lh3.googleusercontent.com/grass-cs/AABkmLeXycde_sYfqi7BUdD3EGKA4RwZaZKNwEpmZrV9iaL8YdEHPhDt37_pqNLPawGLc-BqqQnRbFlI31LT2JrPmjBRHFF82pmxmP1XdM4Fr-RM5Ua-ktJHughJciBl-LB23DzhL-40zA"      # office interior
GBP_DESK = "https://lh3.googleusercontent.com/grass-cs/AABkmLf77eLht6TiqKvbz3KtfnGhMnVSm1iH9bJ8MsyoNvKS-XWaWcWqOL3815b-XDQzH2ebSbRIc70xLeTXw58wMyHMc9oIOOI9YhoRSMWlcdNRzKxSTZH_RvlwlcEGv3LT2E351FXp9BKVhd4"    # front desk with Lake Worth Dentistry logo

STAR = '<svg><use href="#i-star"/></svg>'


def stars(pct):
    return (f'<span class="stars" style="--p:{pct}%" aria-hidden="true">'
            f'<span class="bg">{STAR * 5}</span><span class="fg">{STAR * 5}</span></span>')


TOKENS = {
    "PRACTICE": PRACTICE,
    "PHONE": PHONE,
    "TEL": TEL,
    "BOOK": f'href="{BOOK_URL}" target="_blank" rel="noopener"',
    "BOOK_URL": BOOK_URL,
    "MAPS": MAPS,
    "MAPEMBED": MAP_EMBED,
    "RATING": RATING,
    "COUNT": COUNT,
    "STARS": stars(94),            # 4.7 / 5
    "STARS5": stars(100),
    "G": '<svg class="g-logo"><use href="#g"/></svg>',
    "PHI": '<svg class="ico phone-ico"><use href="#i-phone"/></svg>',
    "SITE": SITE,
    "CF": CF,
    "LOGO": LOGO,
    "LOGO_WHITE": LOGO_WHITE,
    "UN": UN,
    "GBP_OP": GBP_OP,
    "GBP_IN": GBP_IN,
    "GBP_DESK": GBP_DESK,
    "ADDR": "6427 Lake Worth Rd Ste B",
    "CITY": "Greenacres, FL 33463",
}

# ---------------------------------------------------------------- reviews (real, 5-star Google reviews)
REVIEWS = [
    ("Rosalie Fernandez", "I was very nervous about my appointment, but everyone at Lake Worth Dentistry made me feel comfortable "
     "from the moment I walked in. Dr. Macedo was incredibly caring, patient, and reassuring throughout my visit. "
     "I do not have dental insurance, and Leyvis was extremely helpful in discussing my financial options. "
     "The prices were very reasonable. I highly recommend this office to anyone looking for quality dental care."),
    ("Duncan McKinley", "As someone with dentist anxiety, this place put me completely at ease. Gentle dentist, thoughtful "
     "hygienist, and even the assistants and front desk were genuinely polite. Pricing is fair and transparent, and I never "
     "felt taken advantage of. This is my dentist for good now. Also I have no dental insurance and it was not a problem."),
    ("Steven Curtiss", "Bella, the receptionist, Kaya, the hygienist, and Dr. Antezanna were all fantastic. I walked in as a "
     "stranger with my upper full implants loose. I was treated like family. I highly recommend Lake Worth Dentistry for "
     "any dental needs or concerns."),
    ("Marie Armand", "Amazing team. Dr Chelsea and Angie did a great job with my whitening today. Leyvis and everyone else in "
     "the office helped me out to start my treatment and make me feel like family. You need to bring your family here."),
]

AREAS = ["Greenacres FL", "Lake Worth FL", "Lantana FL", "Atlantis FL", "Wellington FL", "Boynton Beach FL",
         "West Palm Beach FL"]

# ---------------------------------------------------------------- page definitions
PAGES = {
    "general": {
        # Recommended WordPress slug: /dentist-lake-worth/
        "out": "dentist-lake-worth.html",
        "lp": "lakeworth-general-new-patient",
        # SEO: title <= 60 chars, description <= 160 chars, keyword + location first, no phone number
        "title": "Lake Worth Dentist in Greenacres, FL | New Patients Welcome",
        "desc": ("Looking for a dentist in Lake Worth or Greenacres, FL? $69 new patient exam & X-rays, gentle "
                 "cleanings, Saturday hours & most PPO plans. Book online today."),
        "og_img": GBP_IN + "=w1200-h630",
        "preload": UN + "1777331903190-341a3dd0441b?auto=format&fit=crop&w=1920&q=75",
        "css": ["base.css"],
        "tokens": {
            "REV_BTNS": '<a class="btn btn-primary btn-xl" {{BOOK}}>{{ICO:cal}}Join Our Happy Patients</a><a class="btn btn-call btn-xl btn-pulse" href="{{TEL}}">{{PHI}}{{PHONE}}</a>',
            "GAL_BTN": '<a class="btn btn-primary btn-xl" {{BOOK}}>{{ICO:cal}}Visit Us — Book Online</a>',
            "INS_LEAD": "Searching for a dentist near me that takes my insurance? We accept a wide range of PPO plans, verify your coverage before you arrive and file every claim for you.",
            "INS_NOINS": "New patients can start with our $69 exam &amp; X-rays special — then pay with card, cash or CareCredit&reg;.",
            "LOC_H2": 'Your Lake Worth Dentist in <em class="acc">Greenacres</em>',
            "LOC_BTNS": '<a class="btn btn-primary" style="flex:1 1 auto" {{BOOK}}>{{ICO:cal}}Book Appointment</a><a class="btn btn-call btn-pulse" style="flex:1 1 auto" href="{{TEL}}">{{PHI}}Call Now</a>',
            "CX_EYEBROW": "Now welcoming new patients",
            "CX_LEAD": "Call us with any question or book your visit online in a few clicks. New patients, Saturday visits and same-day emergencies are always welcome at our Greenacres dental office.",
            "CX_BTNS": '<a class="btn btn-primary btn-xl" {{BOOK}}>{{ICO:cal}}Book Online Now<svg class="ico arr"><use href="#i-right"/></svg></a><a class="btn btn-ghost btn-xl btn-pulse" href="{{TEL}}">{{PHI}}{{PHONE}}</a>',
        },
        "faq": [
            ("Is Lake Worth Dentistry accepting new patients?",
             "Yes. Our Greenacres dental clinic on Lake Worth Road welcomes new patients of all ages, from a child's first check-up to complete smile restoration. Book online or call (561) 771-6540 — new patients can usually be seen quickly."),
            ("Is your dental office open on Saturday?",
             "Yes. We're open Saturday 8 am – 2 pm, plus Monday to Friday 8 am – 5 pm — so if you're searching for a dentist open near me on the weekend, we can help. Saturday appointments fill fast, so book ahead."),
            ("What does the $69 new patient special include?",
             "A comprehensive exam, digital X-rays and a personalized treatment plan for new patients without insurance — for one low price. The offer is for new patients and can't be combined with insurance or other promotions."),
            ("Do you accept my dental insurance?",
             "We accept a wide range of PPO dental insurance plans, file every claim on your behalf and help you maximize your benefits. No insurance? Our $69 new patient special and CareCredit financing keep care affordable."),
            ("Are you in Lake Worth or Greenacres?",
             "Both, practically. Our office is at 6427 Lake Worth Rd Ste B, Greenacres, FL 33463 — right on Lake Worth Road — and we see patients from Lake Worth, Greenacres, Lantana, Atlantis, Wellington, Boynton Beach and West Palm Beach."),
            ("What should I expect at my first visit?",
             "Your first visit takes about an hour. Our hygienist cleans your teeth, then the dentist completes your exam with digital X-rays and builds a personalized treatment plan with you — no surprises."),
            ("Do you treat children and families?",
             "Yes. We're a family dental practice and treat patients of every age, so the whole family can see the same trusted dentist under one roof."),
            ("I'm nervous about the dentist. Can you help?",
             "Absolutely. Many of our 5-star reviews come from patients with dental anxiety. We take our time, explain every step and offer laughing gas and oral sedation so you can relax."),
        ],
    },
    "emergency": {
        # Recommended WordPress slug: /emergency-dentist-lake-worth/
        "out": "emergency-dentist-lake-worth.html",
        "lp": "lakeworth-emergency",
        # SEO: title <= 60 chars, description <= 160 chars, keyword + location first, no phone number
        "title": "Emergency Dentist Lake Worth & Greenacres FL | Same-Day Care",
        "desc": ("Need an emergency dentist in Lake Worth or Greenacres, FL? Same-day urgent dental care, emergency "
                 "tooth extraction & chipped tooth repair. Free emergency exam."),
        "og_img": CF + "/Emergency-Dentist-Greenacres.jpg",
        "preload": CF + "/Emergency-Dentist-Greenacres.jpg",
        "css": ["base.css", "emergency.css"],
        "tokens": {
            "REV_BTNS": '<a class="btn btn-urgent btn-xl btn-pulse" href="{{TEL}}">{{PHI}}Call {{PHONE}}</a><a class="btn btn-primary btn-xl" {{BOOK}}>{{ICO:cal}}Book My Slot for Today</a>',
            "GAL_BTN": '<a class="btn btn-urgent btn-xl btn-pulse" href="{{TEL}}">{{PHI}}Call Our Emergency Dentist</a>',
            "INS_LEAD": "In pain and worried about cost? We accept a wide range of PPO plans and file the claim for you — and new patients get a FREE emergency exam &amp; X-ray.",
            "INS_NOINS": "New patients get a FREE emergency exam &amp; X-ray, and CareCredit&reg; financing makes urgent treatment affordable.",
            "LOC_H2": 'Emergency Dentist Near You in <em class="acc">Lake Worth</em>',
            "LOC_BTNS": '<a class="btn btn-urgent btn-pulse" style="flex:1 1 auto" href="{{TEL}}">{{PHI}}Call Now</a><a class="btn btn-primary" style="flex:1 1 auto" {{BOOK}}>{{ICO:cal}}Book Online</a>',
            "CX_EYEBROW": "In pain right now?",
            "CX_LEAD": "Call us first — we'll talk you through your symptoms and reserve the soonest same-day emergency opening. Weekdays 8 am – 5 pm and Saturdays 8 am – 2 pm.",
            "CX_BTNS": '<a class="btn btn-urgent btn-xl btn-pulse" href="{{TEL}}">{{PHI}}Call {{PHONE}}</a><a class="btn btn-ghost btn-xl" {{BOOK}}>{{ICO:cal}}Book My Slot</a>',
        },
        "faq": [
            ("Do you offer same-day emergency dental appointments?",
             "Yes. We reserve time every day we're open for dental emergencies. Call (561) 771-6540 as early as you can and we'll give you the soonest same-day opening at our Greenacres emergency dental office."),
            ("Can I walk in for a dental emergency?",
             "Please call first, even if you're already on your way. We keep time open for emergencies every day, and a quick call lets us have a chair ready so you're seen as fast as possible."),
            ("Are you open on Saturday for emergencies?",
             "Yes — we're open Saturday 8 am – 2 pm for urgent dental care, as well as Monday to Friday 8 am – 5 pm."),
            ("How much does an emergency dental visit cost?",
             "New patients receive a FREE emergency exam and X-ray to find the source of the pain. We explain your options and the cost of each before any treatment, accept most PPO plans and offer CareCredit financing."),
            ("Can you do an emergency tooth extraction the same day?",
             "Often, yes. If a tooth can't be saved, we perform gentle, fully numbed extractions — including wisdom teeth — and talk you through replacement options such as implants before you leave."),
            ("I chipped a tooth. Is that an emergency?",
             "A small chip can usually wait a day or two, but a large chip, a crack or a tooth in pieces should be seen quickly. Rinse with warm water, save any pieces in milk and call us — we can often repair it with bonding or a crown."),
            ("Should I go to the ER or an emergency dentist?",
             "For a toothache, broken tooth, lost crown, abscess or knocked-out tooth, an emergency dentist can actually treat the problem — hospital ERs generally can't. For a jaw fracture, a severe head injury or swelling that affects breathing or swallowing, call 911 or go to the nearest ER."),
            ("What should I do if a tooth is knocked out?",
             "Pick it up by the crown, rinse it gently without scrubbing, and place it back in the socket or in a cup of milk. Call us right away — a knocked-out tooth has the best chance of being saved when treated quickly."),
        ],
    },
}


def read(*p):
    with open(os.path.join(SRC, *p), encoding="utf-8") as f:
        return f.read()


def render(text, extra=None):
    toks = dict(TOKENS)
    if extra:
        toks.update(extra)
    for _ in range(4):  # includes/tokens can themselves contain includes, icons and tokens
        text = re.sub(r"\{\{INCLUDE:([\w-]+)\}\}", lambda m: read("blocks", m.group(1) + ".html"), text)
        text = re.sub(r"\{\{ICO:([\w-]+)\}\}", lambda m: f'<svg class="ico"><use href="#i-{m.group(1)}"/></svg>', text)
        text = re.sub(r"\{\{([A-Z_0-9]+)\}\}", lambda m: toks.get(m.group(1), m.group(0)), text)
    left = re.findall(r"\{\{[^}]+\}\}", text)
    if left:
        raise SystemExit(f"Unreplaced tokens: {sorted(set(left))}")
    return text


def schema(key, page):
    dentist = {
        "@context": "https://schema.org",
        "@type": "Dentist",
        "@id": "https://www.lakeworth-dentistry.com/#practice",
        "name": PRACTICE,
        "url": "https://www.lakeworth-dentistry.com/",
        "image": [SITE + "/lake-worth/naved_img.jpg", GBP_IN + "=w1200-h900"],
        "telephone": "+1-561-771-6540",
        "priceRange": "$$",
        "foundingDate": "2020",
        "address": {"@type": "PostalAddress", "streetAddress": "6427 Lake Worth Rd Ste B",
                    "addressLocality": "Greenacres", "addressRegion": "FL", "postalCode": "33463",
                    "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": 26.6196008, "longitude": -80.1454285},
        "hasMap": MAPS,
        "areaServed": AREAS,
        "isAcceptingNewPatients": True,
        "paymentAccepted": "Cash, Check, Credit Card, CareCredit, Dental Insurance",
        "openingHoursSpecification": [
            {"@type": "OpeningHoursSpecification",
             "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "opens": "08:00", "closes": "17:00"},
            {"@type": "OpeningHoursSpecification", "dayOfWeek": "Saturday", "opens": "08:00", "closes": "14:00"},
        ],
        "employee": [
            {"@type": "Person", "name": "Dr. Naved Fatmi", "jobTitle": "Lead Dentist, D.M.D.",
             "alumniOf": "University of Florida College of Dentistry"},
            {"@type": "Person", "name": "Dr. Mauricio Antezana", "jobTitle": "General & Cosmetic Dentist, D.M.D."},
            {"@type": "Person", "name": "Dr. Jordan Hekmati", "jobTitle": "Periodontist & Implant Surgeon, D.D.S.",
             "alumniOf": "New York University College of Dentistry"},
        ],
        "aggregateRating": {"@type": "AggregateRating", "ratingValue": RATING, "bestRating": "5",
                            "reviewCount": COUNT},
        "review": [
            {"@type": "Review", "author": {"@type": "Person", "name": n},
             "reviewRating": {"@type": "Rating", "ratingValue": "5", "bestRating": "5"}, "reviewBody": b}
            for n, b in REVIEWS
        ],
    }
    if key == "emergency":
        dentist["medicalSpecialty"] = "Dentistry"
        dentist["availableService"] = [{"@type": "MedicalProcedure", "name": n} for n in (
            "Emergency dental exam", "Emergency tooth extraction", "Emergency root canal",
            "Chipped and broken tooth repair", "Wisdom tooth extraction")]
    faq = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
                       for q, a in page["faq"]],
    }
    return ('<script type="application/ld+json">\n' + json.dumps(dentist, indent=2, ensure_ascii=False)
            + '\n</script>\n<script type="application/ld+json">\n' + json.dumps(faq, indent=2, ensure_ascii=False)
            + "\n</script>")


def faq_html(page):
    out = []
    for i, (q, a) in enumerate(page["faq"]):
        a = a.replace(PHONE, f'<a href="{TEL}">{PHONE}</a>')
        out.append(f'      <details class="rv"{" open" if i == 0 else ""}><summary>{q}<span class="pm" aria-hidden="true"></span>'
                   f'</summary><div class="ans">{a}</div></details>')
    return "\n".join(out)


def build(key):
    page = PAGES[key]
    for field, limit in (("title", 60), ("desc", 160)):
        val = page[field]
        assert len(val) <= limit, f"{key} {field} is {len(val)} chars (max {limit})"
        assert not re.search(r"\d{3}\D{0,2}\d{3}\D?\d{4}", val), f"{key} {field} contains a phone number"
    css = "\n".join(read(c) for c in page["css"])
    page = dict(page, title=htmllib.escape(page["title"]), desc=htmllib.escape(page["desc"]))
    head = f"""<!DOCTYPE html>
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
<title>{page['title']}</title>
<meta name="description" content="{page['desc']}">
<meta name="robots" content="noindex, follow">
<meta name="googlebot" content="noindex, follow">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{PRACTICE}">
<meta property="og:title" content="{page['title']}">
<meta property="og:description" content="{page['desc']}">
<meta property="og:image" content="{page['og_img']}">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{page['title']}">
<meta name="twitter:description" content="{page['desc']}">
<meta name="theme-color" content="#775FA0">
<meta name="format-detection" content="telephone=no">
<link rel="icon" href="{FAVICON}" type="image/png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preconnect" href="https://images.unsplash.com">
<link rel="preconnect" href="https://d11iwgb7g2683x.cloudfront.net">
<link rel="preconnect" href="https://lh3.googleusercontent.com">
<link rel="preload" as="image" href="{page['preload']}">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,600;1,700&family=Raleway:wght@500;600;700;800&display=swap" rel="stylesheet">

<!-- Structured data: practice, Google rating & reviews, FAQ -->
{schema(key, page)}

<style>
{css}
</style>
</head>
<body data-lp="{page['lp']}">
<!-- Google Tag Manager (noscript) -->
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id={GTM_ID}" height="0" width="0" style="display:none;visibility:hidden" title="Google Tag Manager"></iframe></noscript>
<!-- End Google Tag Manager (noscript) -->

<!-- Icon sprite -->
{read('sprite.svg')}
"""
    body = render(read(key + ".html"), {"FAQ_ITEMS": faq_html(page), **page.get("tokens", {})})
    js = render(read("app.js"))
    html = head + body + "\n<script>\n" + js + "</script>\n</body>\n</html>\n"
    with open(os.path.join(HERE, page["out"]), "w", encoding="utf-8") as f:
        f.write(html)
    print(f"wrote {page['out']}  ({len(html) / 1024:.0f} KB)")


if __name__ == "__main__":
    for k in PAGES:
        build(k)
