#!/usr/bin/env python3
"""
Build the two Regency Court Dentistry of Boca Raton Google Ads landing pages.

    regency-court-new-patient-dentist-boca-raton.html   (general / new patient)
    regency-court-emergency-dentist-boca-raton.html     (emergency)

Each output is ONE self-contained HTML file (inline CSS + JS, images hot-linked from
the practice's own website/CDN and Unsplash), so it can be pasted into a WordPress
"Custom HTML" block / blank page template, or uploaded anywhere as-is.

Source lives in src/:
    base.css, emergency.css, app.js, sprite.svg
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

# ---------------------------------------------------------------- practice facts
PRACTICE = "Regency Court Dentistry of Boca Raton"
PHONE = "(561) 979-2003"           # Google Ads tracking number (main site lists a different one)
TEL = "tel:+15619792003"
BOOK_URL = "https://book.allinone.dental/regency-court-dental?referrer_id=3"
MAPS = "https://maps.app.goo.gl/nfztTLTzJS8vadBk7"
MAP_EMBED = ("https://maps.google.com/maps?q=Regency+Court+Dentistry+of+Boca+Raton,"
             "+3003+Yamato+Rd+Ste+C-5,+Boca+Raton,+FL+33434&z=15&output=embed")
GTM_ID = "GTM-N394H9F"
RATING = "4.6"
COUNT = "688"                      # Google Business Profile, Nov 2026 — refresh periodically
SITE = "https://www.regencycourtdentistry.com/wp-content/themes/naved-dental/assets/media"
CF = "https://d11iwgb7g2683x.cloudfront.net/regencycourtdentistry/wp-content/uploads"
LOGO = CF + "/logo.png"
UN = "https://images.unsplash.com/photo-"
GBP_TEAM = "https://lh3.googleusercontent.com/grass-cs/AABkmLdSQOG-qB4AEO6pDHB2Z9klsESsf-gBirGMus3SeqOh_VLqSojD5bijV38dNFt6d3dol6h7EEwuVu9gJMYGEAU1guxg9jtOKADEFIhbzOPJ32w-2EhYX0VAvBFDYtqGL7Pjm-QCTB3wl0cB"

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
    "STARS": stars(92),            # 4.6 / 5
    "STARS5": stars(100),
    "G": '<svg class="g-logo"><use href="#g"/></svg>',
    "PHI": '<svg class="ico phone-ico"><use href="#i-phone"/></svg>',
    "SITE": SITE,
    "CF": CF,
    "LOGO": LOGO,
    "UN": UN,
    "GBP_TEAM": GBP_TEAM,
    "ADDR": "3003 Yamato Rd Ste C-5",
    "CITY": "Boca Raton, FL 33434",
}

# ---------------------------------------------------------------- reviews (real, Google)
REVIEWS = [
    ("Richard Williams", "My experience at this office was top of the line. Upon walking in I was promptly greeted and felt welcome. "
     "Dr. Juliana Marin was very thorough with her oral exam and I left the office knowing everything about my oral health. "
     "Dental hygienist ‘Souzette’ was the best hygienist I have ever been to; I felt zero pain and my teeth were cleaned to my liking."),
    ("Maria Trejo", "I had a wonderful experience at this dental office! The entire staff is incredibly kind, friendly, and welcoming. "
     "Gianna was incredibly patient and helpful while managing my payments and explaining everything clearly. "
     "I highly recommend this clinic to anyone looking for a great dental team."),
]

# ---------------------------------------------------------------- page definitions
PAGES = {
    "general": {
        # Recommended WordPress slug: /dentist-boca-raton/
        "out": "dentist-boca-raton.html",
        "lp": "regency-general-new-patient",
        # SEO: title <= 60 chars, description <= 160 chars, keyword + location first, no phone number
        "title": "Dentist in Boca Raton, FL – New Patients | Regency Court",
        "desc": ("Looking for a dentist in Boca Raton, FL? Regency Court Dentistry welcomes new patients: "
                 "$69 exam & X-rays, teeth cleaning, Saturday hours & most PPO plans."),
        "og_img": UN + "1777331903190-341a3dd0441b?auto=format&fit=crop&w=1200&q=80",
        "preload": UN + "1777331903190-341a3dd0441b?auto=format&fit=crop&w=1920&q=75",
        "css": ["base.css"],
        "tokens": {
            "REV_BTNS": '<a class="btn btn-primary btn-xl" {{BOOK}}>{{ICO:cal}}Join Our Happy Patients</a><a class="btn btn-call btn-xl btn-pulse" href="{{TEL}}">{{PHI}}{{PHONE}}</a>',
            "GAL_BTN": '<a class="btn btn-primary btn-xl" {{BOOK}}>{{ICO:cal}}Visit Us — Book Online</a>',
            "INS_LEAD": "Looking for a dentist near me that takes my insurance? We accept a wide range of PPO plans, verify your coverage before you arrive and file every claim for you.",
            "INS_NOINS": "New patients can start with our $69 exam &amp; X-rays special — then pay with card, cash or CareCredit&reg;.",
            "LOC_H2": 'Your Local Dental Office in <em class="acc">Boca Raton</em>',
            "LOC_BTNS": '<a class="btn btn-primary" style="flex:1 1 auto" {{BOOK}}>{{ICO:cal}}Book Appointment</a><a class="btn btn-call btn-pulse" style="flex:1 1 auto" href="{{TEL}}">{{PHI}}Call Now</a>',
            "CX_EYEBROW": "Now welcoming new patients",
            "CX_LEAD": "Call us with any question or book your visit online in a few clicks. New patients, Saturday visits and same-day emergencies are always welcome at our Boca Raton dental office.",
            "CX_BTNS": '<a class="btn btn-primary btn-xl" {{BOOK}}>{{ICO:cal}}Book Online Now<svg class="ico arr"><use href="#i-right"/></svg></a><a class="btn btn-ghost btn-xl btn-pulse" href="{{TEL}}">{{PHI}}{{PHONE}}</a>',
        },
        "faq": [
            ("Is Regency Court Dentistry accepting new patients in Boca Raton?",
             "Yes. Our Boca Raton dental office welcomes new patients of all ages, from a child's first check-up to complete smile restoration. Book online or call (561) 979-2003 — new patients can usually be seen quickly."),
            ("Is your dentist office open on Saturday?",
             "Yes. We see patients Saturday 8 am – 2 pm, plus Monday to Friday 8 am – 5 pm. Saturday appointments fill fast, so book online or call ahead."),
            ("What does the $69 new patient special include?",
             "A comprehensive exam, digital X-rays and a personalized treatment plan for new patients without insurance — for one low price. The offer is for new patients and can't be combined with insurance or other promotions."),
            ("Do you accept my dental insurance?",
             "We accept a wide range of PPO dental insurance plans, file every claim on your behalf and help you maximize your benefits. Call (561) 979-2003 and we'll verify your plan before your visit."),
            ("How much does a teeth cleaning cost without insurance?",
             "It depends on whether you need a routine cleaning or a deeper cleaning for gum health. Start with our $69 new patient exam and X-rays — we'll give you a clear cost estimate before any treatment, and CareCredit financing is available."),
            ("What should I expect at my first visit?",
             "Your first visit takes about an hour. Our hygienist cleans your teeth, then the doctor completes your exam with digital X-rays and builds a personalized treatment plan with you — no surprises."),
            ("I live in Delray Beach — is your office convenient?",
             "Yes. We're on Yamato Road in Boca Raton, a short drive from Delray Beach, Boynton Beach, Deerfield Beach and Parkland, and many of our patients come from those communities."),
            ("I'm nervous about the dentist. Can you help?",
             "Absolutely. We listen first, explain every step and offer laughing gas and oral sedation so you can relax. Many of our reviews come from patients who used to avoid the dentist."),
        ],
    },
    "emergency": {
        # Recommended WordPress slug: /emergency-dentist-boca-raton/
        "out": "emergency-dentist-boca-raton.html",
        "lp": "regency-emergency",
        # SEO: title <= 60 chars, description <= 160 chars, keyword + location first, no phone number
        "title": "Emergency Dentist Boca Raton, FL | Same-Day | Regency Court",
        "desc": ("Need an emergency dentist in Boca Raton, FL? Same-day urgent dental care, emergency tooth "
                 "extraction & Saturday hours. Free emergency exam for new patients."),
        "og_img": CF + "/Emergency-Dentist-Boca-Raton-1.jpg",
        "preload": CF + "/Emergency-Dentist-Boca-Raton-1.jpg",
        "css": ["base.css", "emergency.css"],
        "tokens": {
            "REV_BTNS": '<a class="btn btn-urgent btn-xl btn-pulse" href="{{TEL}}">{{PHI}}Call {{PHONE}}</a><a class="btn btn-primary btn-xl" {{BOOK}}>{{ICO:cal}}Book My Slot for Today</a>',
            "GAL_BTN": '<a class="btn btn-urgent btn-xl btn-pulse" href="{{TEL}}">{{PHI}}Call Our Emergency Dentist</a>',
            "INS_LEAD": "In pain and worried about cost? We accept a wide range of PPO plans and file the claim for you — and new patients get a FREE emergency exam &amp; X-ray.",
            "INS_NOINS": "New patients get a FREE emergency exam &amp; X-ray, and CareCredit&reg; financing makes urgent treatment affordable.",
            "LOC_H2": 'Emergency Dentist Near You in <em class="acc">Boca Raton</em>',
            "LOC_BTNS": '<a class="btn btn-urgent btn-pulse" style="flex:1 1 auto" href="{{TEL}}">{{PHI}}Call Now</a><a class="btn btn-primary" style="flex:1 1 auto" {{BOOK}}>{{ICO:cal}}Book Online</a>',
            "CX_EYEBROW": "In pain right now?",
            "CX_LEAD": "Call us first — we'll talk you through your symptoms and reserve the soonest same-day emergency opening. Weekdays 8 am – 5 pm and Saturdays 8 am – 2 pm.",
            "CX_BTNS": '<a class="btn btn-urgent btn-xl btn-pulse" href="{{TEL}}">{{PHI}}Call {{PHONE}}</a><a class="btn btn-ghost btn-xl" {{BOOK}}>{{ICO:cal}}Book My Slot</a>',
        },
        "faq": [
            ("Do you offer same-day emergency dental appointments in Boca Raton?",
             "Yes. We reserve time every day we're open for dental emergencies. Call (561) 979-2003 as early as you can and we'll give you the soonest same-day opening."),
            ("Is there a Saturday emergency dentist near me?",
             "Yes — we're open Saturday 8 am – 2 pm for emergency dental care, as well as Monday to Friday 8 am – 5 pm. Call before you come in so we can have a chair ready."),
            ("How much does an emergency dental visit cost?",
             "New patients receive a FREE emergency exam and X-ray to find the source of the pain. We then explain your options and the cost of each before any treatment. We accept most PPO plans and CareCredit financing."),
            ("Can you do an emergency tooth extraction the same day?",
             "Often, yes. If a tooth can't be saved, our doctors perform gentle, numbed extractions — including wisdom teeth — and discuss replacement options such as implants before you leave."),
            ("Should I go to the ER or an emergency dentist?",
             "For a toothache, broken tooth, lost crown, abscess or knocked-out tooth, an emergency dentist can actually treat the problem — hospital ERs generally can't. For a jaw fracture, a severe head injury or swelling that affects breathing or swallowing, call 911 or go to the nearest ER."),
            ("What should I do if a tooth is knocked out?",
             "Pick it up by the crown, rinse it gently without scrubbing, and place it back in the socket or in a cup of milk. Call us right away — a knocked-out tooth has the best chance of being saved when treated quickly."),
            ("Do you see emergency patients from Delray Beach?",
             "Yes. Our office on Yamato Road in Boca Raton is a short drive from Delray Beach, Boynton Beach, Deerfield Beach and Parkland. Call ahead and we'll be ready for you."),
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
        "@id": "https://www.regencycourtdentistry.com/#practice",
        "name": PRACTICE,
        "url": "https://www.regencycourtdentistry.com/",
        "logo": LOGO,
        "image": [LOGO, SITE + "/regency-court/naved_img.jpg"],
        "telephone": "+1-561-979-2003",
        "priceRange": "$$",
        "foundingDate": "2011",
        "address": {"@type": "PostalAddress", "streetAddress": "3003 Yamato Rd Ste C-5",
                    "addressLocality": "Boca Raton", "addressRegion": "FL", "postalCode": "33434",
                    "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": 26.395553, "longitude": -80.1471323},
        "hasMap": MAPS,
        "areaServed": ["Boca Raton FL", "Delray Beach FL", "Boynton Beach FL", "Deerfield Beach FL", "Parkland FL"],
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
            {"@type": "Person", "name": "Dr. Jordan Hekmati", "jobTitle": "Periodontist & Implant Surgeon, D.D.S.",
             "alumniOf": "New York University College of Dentistry"},
            {"@type": "Person", "name": "Dr. Yousof Sinjab", "jobTitle": "Endodontist, D.M.D.",
             "alumniOf": "Nova Southeastern University"},
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
        a = a.replace("(561) 979-2003", f'<a href="{TEL}">(561) 979-2003</a>')
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
<meta name="theme-color" content="#1E211C">
<meta name="format-detection" content="telephone=no">
<link rel="icon" href="{LOGO}" type="image/png">
<link rel="apple-touch-icon" href="{LOGO}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preconnect" href="https://images.unsplash.com">
<link rel="preconnect" href="https://d11iwgb7g2683x.cloudfront.net">
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
