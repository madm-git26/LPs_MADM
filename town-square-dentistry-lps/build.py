#!/usr/bin/env python3
"""
Build the two Town Square Dentistry (Boynton Beach, FL) Google Ads landing pages.

    dentist-boynton-beach.html             general / new patient   (slug /dentist-boynton-beach/)
    emergency-dentist-boynton-beach.html   emergency               (slug /emergency-dentist-boynton-beach/)

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
PRACTICE = "Town Square Dentistry"
PHONE = "(561) 564-0026"           # Google Ads tracking number (main site lists a different one)
TEL = "tel:+15615640026"
BOOK_URL = "https://book.allinone.dental/town-square-dentistry?referrer_id=1"
MAPS = "https://maps.app.goo.gl/hYPqYdSCWkGLrhfM9"
MAP_EMBED = ("https://maps.google.com/maps?q=Town+Square+Dentistry+-+Dentist+Boynton+Beach,"
             "+207+SE+23rd+Ave,+Boynton+Beach,+FL+33435&z=15&output=embed")
GTM_ID = "GTM-MJHBN9L"
RATING = "4.7"
COUNT = "520"                      # Google Business Profile, Nov 2026 — refresh periodically
SITE = "https://www.boyntonbeachtownsquaredentistry.com/wp-content/themes/naved-dental/assets/media"
CF = "https://d11iwgb7g2683x.cloudfront.net/boyntonbeachtownsquaredentistry/wp-content/uploads"
LOGO = _b64("logo.b64")            # the practice's teal logo, embedded
LOGO_WHITE = _b64("logo-white.b64")
FAVICON = _b64("favicon.b64")
UN = "https://images.unsplash.com/photo-"
# Real office photos from the Google Business Profile
GBP_WAIT = "https://lh3.googleusercontent.com/grass-cs/AABkmLe6ngRQG63Raampf1QMfBwTkGR7zHrXOM-1kvxaQ82aeqod7q4lUaxqp4Zmmm8FQyeAH8xz91C0ZnkKD1B1FuibMPoZ5LhZAsdjh1jkBE-e_4xlXzqIsA_X3xsxr2AL0uYV_XmiRaYZivHK"     # waiting room
GBP_OP = "https://lh3.googleusercontent.com/grass-cs/AABkmLdHB982XoutBprsOitawQJH3f6i2U_ffNYTD85cdtMxeQHUZHpDdFgEZFjy44H9ZcBksTA0yoCt9--es9L0z8-tkMSICwfRKXqs5xcpzqUcUXhS2R5aaDBI-r7guF0hn5N9zd5M"       # treatment room
GBP_EXT = "https://lh3.googleusercontent.com/grass-cs/AABkmLd0zTqnk4tjMZR9nJgwrRQEvHRhppgiBOPyMsgb3Cs86u1IujCrcuCbSCZNRjql69BZtjoK-mgB6x8uUXNgRcyVUX83ZxnT08P2BjmiQakoauc_kkcmA2pGrFPZIKDLmSZsNjw-fa7m6wyF"      # building exterior
GBP_HYG = "https://lh3.googleusercontent.com/grass-cs/AABkmLfk57z9JUdBdV8-3Vbki1OfgTPY-j4rGIgWzDjYYZWJUm7HE2q8wyBo7xA_ADQIQnBMOwAGWKawaeaGBn2djSSnVDuB2lg0w6lyrXrnqGmOzi23i5Mu7r3DxvAxfvlYjkkctinTrOglrTJt"      # hygienist in the office

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
    "GBP_WAIT": GBP_WAIT,
    "GBP_OP": GBP_OP,
    "GBP_EXT": GBP_EXT,
    "GBP_HYG": GBP_HYG,
    "ADDR": "207 SE 23rd Ave",
    "CITY": "Boynton Beach, FL 33435",
}

# ---------------------------------------------------------------- reviews (real, 5-star Google reviews)
REVIEWS = [
    ("Tanya Guez-Nisenson", "I had a really positive experience with the staff here. Everyone was warm, welcoming, helpful, and very "
     "accommodating. I had an infection that needed attention, and they even adjusted the schedule so I could have my scaling "
     "done that day, which I really appreciated."),
    ("Roya Gandjei", "I recently had my wisdom teeth removed by Dr. Indictor, and I had a really great experience. I was pretty "
     "nervous going into the procedure, but Dr. Indictor and his assistant, Jessica, were so patient and reassuring that they "
     "helped me feel calm the entire time. The procedure went smoothly and my recovery has been going well."),
    ("R.", "Dr. Finer and her team are personable and do great work! I like the smaller office and everything runs efficiently. "
     "There has been consistent availability around my work schedule."),
    ("Kimberly Chavez", "Very very professional office, everybody is so sweet, they enjoy their job you can tell. This is the "
     "best dental I have had in my whole life. Trust me when I tell you this."),
]

AREAS = ["Boynton Beach FL", "Delray Beach FL", "Boca Raton FL", "Lake Worth FL", "Wellington FL", "Deerfield Beach FL",
         "Highland Beach FL"]

# ---------------------------------------------------------------- page definitions
PAGES = {
    "general": {
        # Recommended WordPress slug: /dentist-boynton-beach/
        "out": "dentist-boynton-beach.html",
        "lp": "townsquare-general-new-patient",
        # SEO: title <= 60 chars, description <= 160 chars, keyword + location first, no phone number
        "title": "Dentist in Boynton Beach, FL | New Patients | Town Square",
        "desc": ("Looking for a dentist in Boynton Beach, FL? Town Square Dentistry offers a $69 new patient exam & "
                 "X-rays, gentle teeth cleaning & most PPO plans. Book online."),
        "og_img": GBP_EXT + "=w1200-h630",
        "preload": UN + "1777331903190-341a3dd0441b?auto=format&fit=crop&w=1920&q=75",
        "css": ["base.css"],
        "tokens": {
            "REV_BTNS": '<a class="btn btn-primary btn-xl" {{BOOK}}>{{ICO:cal}}Join Our Happy Patients</a><a class="btn btn-call btn-xl btn-pulse" href="{{TEL}}">{{PHI}}{{PHONE}}</a>',
            "GAL_BTN": '<a class="btn btn-primary btn-xl" {{BOOK}}>{{ICO:cal}}Visit Us — Book Online</a>',
            "INS_LEAD": "Searching for a dentist near me that takes my insurance? We accept a wide range of PPO plans, verify your coverage before you arrive and file every claim for you.",
            "INS_NOINS": "New patients can start with our $69 exam &amp; X-rays special — then pay with card, cash or CareCredit&reg;.",
            "LOC_H2": 'Your Dentist in <em class="acc">Boynton Beach</em>',
            "LOC_BTNS": '<a class="btn btn-primary" style="flex:1 1 auto" {{BOOK}}>{{ICO:cal}}Book Appointment</a><a class="btn btn-call btn-pulse" style="flex:1 1 auto" href="{{TEL}}">{{PHI}}Call Now</a>',
            "CX_EYEBROW": "Now welcoming new patients",
            "CX_LEAD": "Call us with any question or book your visit online in a few clicks. New patients and same-day emergencies are always welcome at our Boynton Beach dental office.",
            "CX_BTNS": '<a class="btn btn-primary btn-xl" {{BOOK}}>{{ICO:cal}}Book Online Now<svg class="ico arr"><use href="#i-right"/></svg></a><a class="btn btn-ghost btn-xl btn-pulse" href="{{TEL}}">{{PHI}}{{PHONE}}</a>',
        },
        "faq": [
            ("Is Town Square Dentistry accepting new patients in Boynton Beach?",
             "Yes. Our Boynton Beach dental office welcomes new patients of all ages, from a child's first check-up to complete smile restoration. Book online or call (561) 564-0026 — new patients can usually be seen quickly."),
            ("How quickly can I get a dentist appointment?",
             "Usually within days, often sooner. Book your dentist appointment online in a few clicks — at any time of day — or call us and we'll find a time that fits your schedule."),
            ("What does the $69 new patient special include?",
             "A comprehensive exam, digital X-rays and a personalized treatment plan for new patients without insurance — for one low price. The offer is for new patients and can't be combined with insurance or other promotions."),
            ("Do you accept my dental insurance?",
             "We accept a wide range of PPO dental insurance plans, file every claim on your behalf and help you maximize your benefits. No insurance? Our $69 new patient special and CareCredit financing keep care affordable."),
            ("How much does a teeth cleaning cost without insurance?",
             "It depends on whether you need a routine cleaning or a deeper cleaning for gum health. Start with our $69 new patient exam and X-rays — we'll give you a clear cost estimate before any treatment."),
            ("Where is your dental office?",
             "We're at 207 SE 23rd Ave, Boynton Beach, FL 33435, and see patients from Boynton Beach, Delray Beach, Boca Raton, Lake Worth, Wellington and Highland Beach — a convenient dentist near Boynton Beach, FL for the whole family."),
            ("What should I expect at my first visit?",
             "Your first visit takes about an hour. Our hygienist cleans your teeth, then the dentist completes your exam with digital X-rays and builds a personalized treatment plan with you — no surprises."),
            ("I'm nervous about the dentist. Can you help?",
             "Absolutely. Many of our 5-star reviews come from nervous patients. We take our time, explain every step and offer laughing gas and oral sedation so you can relax."),
        ],
    },
    "emergency": {
        # Recommended WordPress slug: /emergency-dentist-boynton-beach/
        "out": "emergency-dentist-boynton-beach.html",
        "lp": "townsquare-emergency",
        # SEO: title <= 60 chars, description <= 160 chars, keyword + location first, no phone number
        "title": "Emergency Dentist Boynton Beach, FL | Same-Day | Town Square",
        "desc": ("Need an emergency dentist in Boynton Beach, FL? Same-day urgent dental care, emergency tooth extraction "
                 "& root canal treatment. Free emergency exam & X-ray."),
        "og_img": CF + "/Emergency-Dentist-Boynton-Beach.jpg",
        "preload": CF + "/Emergency-Dentist-Boynton-Beach.jpg",
        "css": ["base.css", "emergency.css"],
        "tokens": {
            "REV_BTNS": '<a class="btn btn-urgent btn-xl btn-pulse" href="{{TEL}}">{{PHI}}Call {{PHONE}}</a><a class="btn btn-primary btn-xl" {{BOOK}}>{{ICO:cal}}Book My Slot for Today</a>',
            "GAL_BTN": '<a class="btn btn-urgent btn-xl btn-pulse" href="{{TEL}}">{{PHI}}Call Our Emergency Dentist</a>',
            "INS_LEAD": "In pain and worried about cost? We accept a wide range of PPO plans and file the claim for you — and new patients get a FREE emergency exam &amp; X-ray.",
            "INS_NOINS": "New patients get a FREE emergency exam &amp; X-ray, and CareCredit&reg; financing makes urgent treatment affordable.",
            "LOC_H2": 'Emergency Dentist Near You in <em class="acc">Boynton Beach</em>',
            "LOC_BTNS": '<a class="btn btn-urgent btn-pulse" style="flex:1 1 auto" href="{{TEL}}">{{PHI}}Call Now</a><a class="btn btn-primary" style="flex:1 1 auto" {{BOOK}}>{{ICO:cal}}Book Online</a>',
            "CX_EYEBROW": "In pain right now?",
            "CX_LEAD": "Call us first — we'll talk you through your symptoms and reserve the soonest same-day emergency opening. We're open Monday to Friday, 8 am – 5 pm.",
            "CX_BTNS": '<a class="btn btn-urgent btn-xl btn-pulse" href="{{TEL}}">{{PHI}}Call {{PHONE}}</a><a class="btn btn-ghost btn-xl" {{BOOK}}>{{ICO:cal}}Book My Slot</a>',
        },
        "faq": [
            ("Do you offer same-day emergency dental appointments in Boynton Beach?",
             "Yes. We reserve time every day we're open for dental emergencies. Call (561) 564-0026 as early as you can and we'll give you the soonest same-day opening."),
            ("Can I walk in for a dental emergency?",
             "Please call first, even if you're already on your way. We keep time open for emergencies every day, and a quick call lets us have a chair ready so you're seen as fast as possible."),
            ("How much does an emergency dental visit cost?",
             "New patients receive a FREE emergency exam and X-ray to find the source of the pain. We explain your options and the cost of each before any treatment, accept most PPO plans and offer CareCredit financing."),
            ("Can you do an emergency tooth extraction the same day?",
             "Often, yes. If a tooth can't be saved, we perform gentle, fully numbed extractions — including wisdom teeth — and talk you through replacement options such as implants before you leave."),
            ("Do you offer emergency root canal treatment?",
             "Yes. A root canal removes the infection, relieves the pain and saves your natural tooth. We'll examine the tooth with X-rays and, when possible, start treatment the same visit."),
            ("Should I go to the ER or an emergency dentist?",
             "For a toothache, broken tooth, lost crown, abscess or knocked-out tooth, an emergency dentist can actually treat the problem — hospital ERs generally can't. For a jaw fracture, a severe head injury or swelling that affects breathing or swallowing, call 911 or go to the nearest ER."),
            ("What should I do if a tooth is knocked out?",
             "Pick it up by the crown, rinse it gently without scrubbing, and place it back in the socket or in a cup of milk. Call us right away — a knocked-out tooth has the best chance of being saved when treated quickly."),
            ("I'm anxious and in pain. Can you help me relax?",
             "Yes. Pain relief comes first. We use local anesthetic and offer laughing gas and oral sedation for anxious patients, and we explain every step before we begin."),
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
        "@id": "https://www.boyntonbeachtownsquaredentistry.com/#practice",
        "name": PRACTICE,
        "url": "https://www.boyntonbeachtownsquaredentistry.com/",
        "image": [GBP_EXT + "=w1200-h760", GBP_WAIT + "=w1200-h900"],
        "telephone": "+1-561-564-0026",
        "priceRange": "$$",
        "foundingDate": "2018",
        "address": {"@type": "PostalAddress", "streetAddress": "207 SE 23rd Ave",
                    "addressLocality": "Boynton Beach", "addressRegion": "FL", "postalCode": "33435",
                    "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": 26.5074633, "longitude": -80.0643806},
        "hasMap": MAPS,
        "areaServed": AREAS,
        "isAcceptingNewPatients": True,
        "paymentAccepted": "Cash, Check, Credit Card, CareCredit, Dental Insurance",
        "openingHoursSpecification": [
            {"@type": "OpeningHoursSpecification",
             "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "opens": "08:00", "closes": "17:00"},
        ],
        "employee": [
            {"@type": "Person", "name": "Dr. Naved Fatmi", "jobTitle": "Lead Dentist, D.M.D.",
             "alumniOf": "University of Florida College of Dentistry"},
            {"@type": "Person", "name": "Dr. Mitchell Indictor", "jobTitle": "General Dentist, D.D.S."},
            {"@type": "Person", "name": "Dr. Libby Finer", "jobTitle": "General Dentist, D.M.D.",
             "alumniOf": "Nova Southeastern University College of Dental Medicine"},
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
            "Broken tooth repair", "Wisdom tooth extraction")]
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
<meta name="theme-color" content="#3F9CBB">
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
