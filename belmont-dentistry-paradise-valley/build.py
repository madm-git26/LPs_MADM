#!/usr/bin/env python3
"""
Build the Belmont Dentistry Paradise Valley Google Ads landing pages.

    new-patients-paradise-valley.html        (new patient / general dentist)
    emergency-dentist-paradise-valley.html   (emergency dentist)
    thank-you-paradise-valley.html           (shared post-booking page)

The pages share the Belmont design system (assets/css/belmont.css, assets/js/lp.js)
and add a Paradise Valley motion layer on top (assets/css/pv-motion.css,
assets/js/pv-motion.js): 3D rating coin, sliding headline, magnetic/ripple
buttons, scroll progress, scroll-driven 3D reveals, parallax and a
before/after smile slider.

and a single-file copy of each in standalone/ (CSS, JS and images inlined).

All copy lives in this file. Edit the strings and re-run:

    python3 build.py

Editing the generated .html directly is fine too; a rebuild overwrites it.
"""

import base64
import html
import json
import mimetypes
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent

# --------------------------------------------------------------------------
# Practice facts — Paradise Valley office only (15255 N 40th St, Phoenix)
# --------------------------------------------------------------------------
PRACTICE = "Belmont Dentistry Paradise Valley"
PHONE = "(480) 530-3812"          # Google Ads tracking number
TEL = "tel:+14805303812"
BOOK_URL = "https://book.allinone.dental/complete-dental-care?referrer_id=4"
GMB_URL = "https://maps.app.goo.gl/zwTqk5W6PRVpaw7w6"
MAP_EMBED = ("https://www.google.com/maps/embed?pb=!1m14!1m8!1m3!1d26577.902293374074!2d-111.994516!3d33.625076"
             "!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x872b7303f06e49a3%3A0xd0b3cb4e29b8048"
             "!2sComplete%20Dental%20Care%20Paradise%20Valley!5e0!3m2!1sen!2sus!4v1790601096144!5m2!1sen!2sus")
STREET = "15255 N 40th St, STE 141"
CITY_LINE = "Phoenix, AZ 85032"
ADDRESS = f"{STREET}, {CITY_LINE}"
RATING = "4.9"
REVIEW_COUNT = "508"          # Google, Paradise Valley listing — read Oct 2026
SITE = "https://www.belmontdentistry.com"
LP_BASE = SITE + "/paradise-valley-az/lp/"
CANONICAL = {}

BOOK = f'href="{BOOK_URL}" target="_blank" rel="noopener"'

# Google Tag Manager — script goes first in <head>, noscript first in <body>
GTM_ID = "GTM-PKC6XXJ"
GTM_HEAD = ("<!-- Google Tag Manager -->\n"
            "<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':\n"
            "new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],\n"
            "j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=\n"
            "'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);\n"
            f"}})(window,document,'script','dataLayer','{GTM_ID}');</script>\n"
            "<!-- End Google Tag Manager -->")
GTM_BODY = ("<!-- Google Tag Manager (noscript) -->\n"
            f'<noscript><iframe src="https://www.googletagmanager.com/ns.html?id={GTM_ID}" '
            'height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>\n'
            "<!-- End Google Tag Manager (noscript) -->")
CALL = f'href="{TEL}"'

HOURS = [  # (schema day, label, display, js day index) — from belmontdentistry.com/paradise-valley-az/
    ("Monday", "Monday", "8:00 am – 5:00 pm", 1),
    ("Tuesday", "Tuesday", "8:00 am – 5:00 pm", 2),
    ("Wednesday", "Wednesday", "8:00 am – 5:00 pm", 3),
    ("Thursday", "Thursday", "8:00 am – 5:00 pm", 4),
    ("Friday", "Friday", "8:00 am – 5:00 pm", 5),
    ("Saturday", "Saturday", "Closed", 6),
    ("Sunday", "Sunday", "Closed", 0),
]

# --------------------------------------------------------------------------
# Icons (24px stroke icons, defined once and referenced with <use>)
# --------------------------------------------------------------------------
ICONS = {
    "phone": '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/>',
    "calendar": '<rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/><path d="m9 16 2 2 4-4"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>',
    "sparkles": '<path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3Z"/>',
    "heart": '<path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>',
    "zap": '<path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/>',
    "alert": '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4M12 17h.01"/>',
    "card": '<rect x="2" y="5" width="20" height="14" rx="2"/><path d="M2 10h20"/>',
    "award": '<circle cx="12" cy="8" r="6"/><path d="M15.48 12.89 17 22l-5-3-5 3 1.52-9.11"/>',
    "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
    "headphones": '<path d="M3 14h3a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-7a9 9 0 0 1 18 0v7a2 2 0 0 1-2 2h-1a2 2 0 0 1-2-2v-3a2 2 0 0 1 2-2h3"/>',
    "scan": '<path d="M3 7V5a2 2 0 0 1 2-2h2M17 3h2a2 2 0 0 1 2 2v2M21 17v2a2 2 0 0 1-2 2h-2M7 21H5a2 2 0 0 1-2-2v-2"/><path d="M7 12h10"/>',
    "droplet": '<path d="M12 22a7 7 0 0 0 7-7c0-2-1-3.9-3-5.5s-3.5-4-4-6.5c-.5 2.5-2 4.9-4 6.5C6 11.1 5 13 5 15a7 7 0 0 0 7 7z"/>',
    "down": '<path d="m6 9 6 6 6-6"/>',
    "left": '<path d="m15 18-6-6 6-6"/>',
    "right": '<path d="m9 18 6-6-6-6"/>',
    "arrow": '<path d="M5 12h14M12 5l7 7-7 7"/>',
    "play": '<path d="M7 4v16l13-8z"/>',
    "pause": '<path d="M7 4h3v16H7zM14 4h3v16h-3z"/>',
    "nav": '<path d="M3 11 22 2l-9 19-2-8-8-2z"/>',
    "smile": '<circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2M9 9h.01M15 9h.01"/>',
    "dollar": '<path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>',
    "flame": '<path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.07-2.14-.22-4.05 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.15.43-2.29 1-3a2.5 2.5 0 0 0 2.5 2.5z"/>',
    "tooth": '<path d="M7 3c-2.5 0-4 2-4 4.5 0 2 .7 3.3 1.3 4.6.6 1.4.7 3 1 4.9.3 2 .8 4 2.2 4 1.6 0 1.7-2.4 2.2-4.2.3-1.1.9-1.8 2.3-1.8s2 .7 2.3 1.8c.5 1.8.6 4.2 2.2 4.2 1.4 0 1.9-2 2.2-4 .3-1.9.4-3.5 1-4.9.6-1.3 1.3-2.6 1.3-4.6C21 5 19.5 3 17 3c-2 0-3 1-5 1S9 3 7 3z"/>',
    "broken": '<path d="M7 3c-2.5 0-4 2-4 4.5 0 2 .7 3.3 1.3 4.6.6 1.4.7 3 1 4.9.3 2 .8 4 2.2 4 1.6 0 1.7-2.4 2.2-4.2.3-1.1.9-1.8 2.3-1.8s2 .7 2.3 1.8c.5 1.8.6 4.2 2.2 4.2 1.4 0 1.9-2 2.2-4 .3-1.9.4-3.5 1-4.9.6-1.3 1.3-2.6 1.3-4.6C21 5 19.5 3 17 3c-2 0-3 1-5 1S9 3 7 3z"/><path d="m12 4-1.5 3.5L13 9l-1.5 3.5"/>',
    "coffee": '<path d="M17 8h1a4 4 0 1 1 0 8h-1M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4ZM6 2v2M10 2v2M14 2v2"/>',
    "monitor": '<rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/>',
    "x": '<circle cx="12" cy="12" r="10"/><path d="m15 9-6 6M9 9l6 6"/>',
    "snow": '<path d="M2 12h20M12 2v20m8-6-4-4 4-4M4 8l4 4-4 4M16 4l-4 4-4-4M8 20l4-4 4 4"/>',
    "siren": '<path d="M7 18v-6a5 5 0 1 1 10 0v6M5 21a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-1a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2zM21 12h1M18.5 4.5 18 5M2 12h1M12 2v1M4.93 4.93l.71.71M12 12v6"/>',
    "parking": '<rect x="3" y="3" width="18" height="18" rx="2"/><path d="M9 17V7h4a3 3 0 0 1 0 6H9"/>',
    "child": '<circle cx="12" cy="5" r="2.5"/><path d="M9 22v-6l-3-1 2-6h8l2 6-3 1v6"/>',
    "id": '<rect x="2" y="5" width="20" height="14" rx="2"/><circle cx="8" cy="12" r="2.5"/><path d="M14 10h4M14 14h4"/>',
    "pill": '<path d="m10.5 20.5 10-10a4.95 4.95 0 1 0-7-7l-10 10a4.95 4.95 0 1 0 7 7ZM8.5 8.5l7 7"/>',
    "file": '<path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/><path d="M14 2v6h6M8 13h8M8 17h5"/>',
    "blanket": '<path d="M3 7h18v10H3z"/><path d="M3 12h18M8 7v10"/>',
    "laser": '<path d="M2 12h6M10 12h1M13 12h1M16 12h6"/><path d="m18 8 4 4-4 4"/>',
    "star": '<path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>',
}


def sprite():
    out = []
    for name, body in ICONS.items():
        if name == "star":
            out.append(f'<symbol id="i-{name}" viewBox="0 0 24 24"><g fill="currentColor" stroke="none">{body}</g></symbol>')
        else:
            out.append(f'<symbol id="i-{name}" viewBox="0 0 24 24">{body}</symbol>')
    return '<svg xmlns="http://www.w3.org/2000/svg" style="display:none" aria-hidden="true">' + "".join(out) + "</svg>"


def ic(name, cls=""):
    c = f"icon {cls}".strip()
    return f'<svg class="{c}" aria-hidden="true"><use href="#i-{name}"/></svg>'


def stars():
    return '<span class="stars" aria-hidden="true">' + "".join(ic("star") for _ in range(5)) + "</span>"


GOOGLE_G = ('<svg viewBox="0 0 48 48" aria-hidden="true"><path fill="#FFC107" d="M43.6 20.1H42V20H24v8h11.3C33.7 32.7 29.2 36 24 36c-6.6 0-12-5.4-12-12s5.4-12 12-12c3.1 0 5.8 1.2 7.9 3.1l5.7-5.7C34 6.1 29.3 4 24 4 12.9 4 4 12.9 4 24s8.9 20 20 20 20-8.9 20-20c0-1.3-.1-2.6-.4-3.9z"/>'
            '<path fill="#FF3D00" d="m6.3 14.7 6.6 4.8C14.7 15.1 19 12 24 12c3.1 0 5.8 1.2 7.9 3.1l5.7-5.7C34 6.1 29.3 4 24 4 16.3 4 9.7 8.3 6.3 14.7z"/>'
            '<path fill="#4CAF50" d="M24 44c5.2 0 9.9-2 13.4-5.2l-6.2-5.2C29.2 35.1 26.7 36 24 36c-5.2 0-9.6-3.3-11.3-8l-6.5 5C9.5 39.6 16.2 44 24 44z"/>'
            '<path fill="#1976D2" d="M43.6 20.1H42V20H24v8h11.3c-.8 2.2-2.2 4.2-4.1 5.6l6.2 5.2C37 39.2 44 34 44 24c0-1.3-.1-2.6-.4-3.9z"/></svg>')


def rating_pill(cta="rating"):
    return (f'<a class="rating-pill" href="{GMB_URL}" target="_blank" rel="noopener" data-cta="{cta}" '
            f'aria-label="Rated {RATING} out of 5 from {REVIEW_COUNT} Google reviews — read them on Google">'
            f'<span class="g">{GOOGLE_G}</span><b>{RATING}</b>{stars()}<small>{REVIEW_COUNT} Google reviews</small></a>')


def btn_book(label="Book Online", cls="btn btn-gold", cta=""):
    return f'<a class="{cls}" {BOOK} data-cta="{cta}">{ic("calendar")}<span>{label}</span></a>'


def btn_call(label=None, cls="btn btn-dark", cta="", ring=True):
    label = label or f"Call {PHONE}"
    return f'<a class="{cls}" {CALL} data-cta="{cta}">{ic("phone", "ring-icon" if ring else "")}<span>{label}</span></a>'


def two(long, short):
    """Full button label on desktop, short label on phones (where CTAs sit side by side)."""
    return f'<span class="lbl-long">{long}</span><span class="lbl-short">{short}</span>'


def section_cta(page, cta, note=None, dark=False):
    """Every section ends with a CTA pair. Emergency pages lead with the phone."""
    if page == "em":
        first = btn_call(two(f"Call Now {PHONE}", "Call Now"), "btn btn-red btn-lg btn-pulse", cta)
        second = btn_book(two("Book Online", "Book Online"), "btn btn-ghost btn-lg" if dark else "btn btn-outline btn-lg", cta)
    else:
        first = btn_book(two("Book Your Visit Online", "Book Online"), "btn btn-gold btn-lg", cta)
        second = btn_call(two(f"Call {PHONE}", "Call Us"), "btn btn-ghost btn-lg" if dark else "btn btn-outline btn-lg", cta)
    n = f'<p class="note">{note}</p>' if note else ""
    return f'<div class="section-cta" data-reveal>{first}{second}{n}</div>'


def carousel(slides, label, cls="m-carousel", track_cls="", auto=False):
    """Swipe carousel (arrows + dots). With m-carousel it is a plain grid above 760px."""
    return (f'<div class="carousel {cls}" data-carousel{" data-auto" if auto else ""}><div class="carousel-track {track_cls}">{slides}</div>'
            f'<div class="carousel-nav"><button class="carousel-btn" data-prev aria-label="Previous {label}">{ic("left")}</button><div class="dots"></div>'
            f'<button class="carousel-btn" data-next aria-label="Next {label}">{ic("right")}</button></div></div>')


def head_block(kicker, title, lead=None, cls="section-head"):
    p = f"<p>{lead}</p>" if lead else ""
    return f'<div class="{cls}" data-reveal><span class="kicker">{kicker}</span><h2>{title}</h2>{p}</div>'


def esc(s):
    return html.escape(s, quote=True)


# --------------------------------------------------------------------------
# Real Google reviews of the Paradise Valley office (verbatim, from the site's
# Paradise Valley Google review feed, Oct 2026). Reviews that name the previous
# owner or the old practice name are left out.
# --------------------------------------------------------------------------
REVIEWS = {
    "edgar": ("Edgar Ponce", "New patient",
              "From the moment I walked in the staff was friendly and made it feel like I was an existing customer. Experience was great and the facility was very clean and organized! If you are looking for your new dental care spot look no further!"),
    "hannah": ("hannah stoddart", "Dr. Mohan",
               "Absolutely loved visiting Dr. Mohan, she was so knowledgeable and helpful. The place itself is super clean with modern technology and all the staff members were so kind and friendly. Best dentist visit I’ve ever had by far!"),
    "james": ("James Chapman", "Dental anxiety",
              "I had been avoiding essential dental work due to previous negative experiences. Dr.P and his team not only alleviated the stress but empowered me by actively including me in the treatment plan."),
    "lovell": ("Lovell George", "Dr. Sandhu",
               "Wonderful and friendly staff!! Dr P. Was great, and explained everything well. Tierney is a wonderful hygienist! I highly recommend!!"),
    "kathleen": ("Kathleen Benton", "Modern technology",
                 "Great office from the state of the art technology, to the friendly and very knowledgeable staff including a painless cleaning from the hygienist and a very smart and caring dentist. This office has it all going on! I highly recommend it!"),
    "angelica": ("Angelica Livas", "Quick appointments",
                 "I’ve been coming here since they opened and it’s been a great experience with everyone in this office! They’re able to get me in quick every time I have a change in schedule."),
    "michael": ("Michael Czapka", "Clear explanations",
                "Excellent service and patient care, thoroughly explained everything that was occurring and made sure I was informed during the entire appointment."),
    "medina": ("J Medina", "Clean &amp; welcoming",
               "Great dental office. Everyone is friendly, professional, and welcoming. The office is also very clean and comfortable."),
    "terri": ("Terri Foster", "Caring team",
              "Awesome dental care is available and I just found the place. If you’re looking for a dental office that cares and has your interest at heart, this is the place for you."),
    "anika": ("anika fournier", "Comfortable visit",
              "Love love love this place, the staff are so friendly and make you feel very comfortable. Could not recommend enough."),
}


def review_card(key):
    name, tag, text = REVIEWS[key]
    initials = "".join(w[0] for w in name.split()[:2]).upper()
    return (f'<figure class="review"><span class="quote-mark" aria-hidden="true">“</span>{stars()}'
            f'<span class="tagline">{tag}</span><blockquote>{text}</blockquote>'
            f'<footer><span class="avatar" aria-hidden="true">{initials}</span><div><strong>{name}</strong>'
            f'<small>{GOOGLE_G} Google review · Paradise Valley</small></div></footer></figure>')


# --------------------------------------------------------------------------
# Shared sections
# --------------------------------------------------------------------------
def topbar(page):
    if page == "em":
        return (f'<div class="topbar urgent"><div class="shell"><a {CALL} data-cta="topbar">{ic("siren")}'
                f'Toothache, broken tooth or swelling? Same-day emergency appointments — Call {PHONE}</a></div></div>')
    return (f'<div class="topbar"><div class="shell">'
            f'<a href="{GMB_URL}" target="_blank" rel="noopener" data-cta="topbar">{ic("pin")}{ADDRESS}</a>'
            f'<span>{ic("clock")}Open Monday–Friday, 8 am–5 pm</span>'
            f'<a href="{GMB_URL}" target="_blank" rel="noopener" data-cta="topbar">{ic("star")}{RATING} stars · {REVIEW_COUNT} Google reviews</a>'
            f'</div></div>')


def site_header(page):
    nav = [("services", "Services"), ("doctors", "Doctors"), ("insurance", "Insurance"), ("reviews", "Reviews"), ("faq", "FAQ"), ("location", "Location")]
    if page == "em":
        nav[0] = ("emergencies", "Emergencies")
    if page == "ty":
        nav = [("next-steps", "Next Steps"), ("dentists", "Your Dentists"), ("location", "Directions")]
    links = "".join(f'<a href="#{a}">{t}</a>' for a, t in nav)
    call_cls = "btn btn-red header-phone-em" if page == "em" else "btn header-phone"
    second = (f'<a class="btn btn-gold btn-book-head" href="{GMB_URL}" target="_blank" rel="noopener" data-cta="header">{ic("nav")}<span>Directions</span></a>'
              if page == "ty" else btn_book("Book Online", "btn btn-gold btn-book-head", "header"))
    return (f'<header class="site-header"><div class="shell">'
            f'<a class="brand" href="#top" aria-label="Belmont Dentistry Paradise Valley — back to top"><img src="assets/img/logo-belmont-dentistry.webp" width="520" height="240" alt="Belmont Dentistry — Complete Dental Care"></a>'
            f'<nav class="main-nav" aria-label="Page sections">{links}</nav>'
            f'<div class="header-actions"><a class="{call_cls}" {CALL} data-cta="header">{ic("phone", "ring-icon")}<span>{PHONE}</span></a>'
            f'{second}</div>'
            f'</div></header>')


def marquee(items, red=False):
    spans = "".join(f"<span>{t}</span>" for t in items)
    return f'<div class="marquee{" red" if red else ""}" aria-hidden="true"><div class="marquee-track">{spans}{spans}</div></div>'


def stats(items):
    cells = "".join(f'<div class="stat"><b>{b}</b><span>{s}</span></div>' for b, s in items)
    return f'<div class="stats" role="region" aria-label="At a glance"><div class="shell"><div class="stats-grid" data-reveal>{cells}</div></div></div>'


DOCTORS = [  # (name, suffix, role, credential line, photo, bio, tags, short name)
    ("Dr. Puneet Sandhu", "DDS", "Owner Dentist", "DDS · UCLA School of Dentistry", "assets/img/img-Dr-Puneet-Sandhu.webp",
     "An easygoing family and cosmetic dentist and a Spear Education faculty member. Trained in full-mouth reconstruction, he treats every patient as a partner in their care — never a chart number.",
     ["Spear Faculty Club", "Full-Mouth Reconstruction", "Int’l Dental Implant Assoc.", "Family &amp; Cosmetic Care"], "Dr. Sandhu"),
    ("Dr. Sugandha Mohan", "", "Dentist", "BDS · Advanced Training, New York University", "assets/img/img-Dr-Mohan-DDS.webp",
     "A restorative and comprehensive-care dentist serving Phoenix since 2015. Known for her warm chairside manner and meticulous attention to detail, she looks at the full picture of your oral health — not just the tooth in front of her.",
     ["NYU Restorative Training", "Comprehensive Planning", "Serving Phoenix Since 2015"], "Dr. Mohan"),
]


def full_name(name, suffix):
    return f"{name}, {suffix}" if suffix else name


def doctors_section(page, cls=""):
    cards = []
    for i, (name, suffix, role, cred, img, bio, tags, first) in enumerate(DOCTORS):
        t = "".join(f"<li>{x}</li>" for x in tags)
        cards.append(
            f'<article class="doc tilt" data-tilt="6" data-reveal style="--d:{i * .12:.2f}s">'
            f'<div class="doc-photo"><img src="{img}" width="467" height="611" loading="lazy" alt="{full_name(name, suffix)} — dentist at {PRACTICE}"><span class="doc-role">{role}</span></div>'
            f'<div class="doc-body"><h3>{full_name(name, suffix)}</h3><div class="cred">{cred}</div><p>{bio}</p><ul class="doc-tags">{t}</ul>'
            f'{btn_book("Book with " + first, "btn btn-outline btn-block", "doctor")}</div></article>')
    title = ("Meet Your Paradise Valley Dentists. <em class=\"gold\">One Welcoming Office.</em>" if page == "np"
             else "Experienced Emergency Dentists <em class=\"gold\">You Can Trust</em>")
    lead = ("Two experienced doctors, one welcoming office, and a team that treats every patient like family."
            if page == "np" else
            "When you’re in pain you want an experienced dentist who explains what’s wrong and fixes it — from emergency extractions to root canals and crown repairs.")
    return (f'<section class="section {cls}" id="doctors"><div class="shell">{head_block("Meet Your Dentists", title, lead)}'
            f'<div class="carousel m-carousel cols-2 doc-carousel" data-carousel><div class="carousel-track">{"".join(cards)}</div>'
            f'<div class="carousel-nav"><button class="carousel-btn" data-prev aria-label="Previous dentist">{ic("left")}</button><div class="dots"></div><button class="carousel-btn" data-next aria-label="Next dentist">{ic("right")}</button></div></div>'
            f'{section_cta(page, "doctors")}</div></section>')


def awards_section(page):
    badges = [
        ("star", f"{RATING}★ on Google", f"Average rating from {REVIEW_COUNT} Google reviews of our Paradise Valley office"),
        ("award", "Spear Faculty Club", "Dr. Puneet Sandhu is a faculty member of Spear Education, the world’s largest dental education company"),
        ("heart", "NYU Advanced Training", "Dr. Sugandha Mohan trained at New York University in comprehensive planning and restorative dentistry"),
    ]
    b = "".join(f'<div class="badge-card tilt" data-tilt="5" data-reveal style="--d:{i * .1:.1f}s"><span class="badge-medal">{ic(icn)}</span><div><strong>{t}</strong><span>{s}</span></div></div>'
                for i, (icn, t, s) in enumerate(badges))
    logos = [("logo-invisialign.svg", "Invisalign provider", 360, 86), ("logo-spear-faculty-club.svg", "Spear Faculty Club", 360, 86),
             ("logo-ada.svg", "American Dental Association", 193, 86), ("logo-Ada-arizona-dental-association.png", "Arizona Dental Association", 570, 172),
             ("logo-CADSF.png", "Central Arizona Dental Society Foundation", 424, 172), ("logo-idia.webp", "International Dental Implant Association", 200, 158)]
    l = "".join(f'<img src="assets/img/{f}" alt="{a}" width="{w}" height="{h}" loading="lazy">' for f, a, w, h in logos)
    l += "".join(f'<img class="dup" src="assets/img/{f}" alt="" aria-hidden="true" width="{w}" height="{h}" loading="lazy">' for f, a, w, h in logos)
    title = "Awards, Affiliations &amp; <em class=\"gold\">5-Star Care</em>"
    return (f'<section class="awards" aria-label="Awards and affiliations"><div class="shell">'
            f'<div class="awards-head" data-reveal><span class="kicker">Recognized &amp; Trusted</span><h2>{title}</h2>'
            f'<p>Advanced training, professional memberships and hundreds of happy Phoenix and Paradise Valley patients.</p></div>'
            f'{carousel(b, "award", "m-carousel cols-3 badge-carousel", "badges")}'
            f'<div class="logo-strip" data-reveal><div class="logo-row">{l}</div></div>{section_cta(page, "awards")}</div></section>')


def insurance_section(page):
    ppo = ["In-network with several PPO plans", "We file claims for most other plans", "Benefits verified before treatment", "Help planning around your annual maximum"]
    plan = ["2 check-ups &amp; 2 regular cleanings", "1 emergency exam &amp; all X-rays", "50% off Cone Beam CT scans", "20% off all services — no claim forms"]
    cc = ["Pay over time instead of all at once", "Low or no interest options*", "Ideal for implants &amp; smile makeovers", "Decisions often within minutes"]

    def lst(items):
        return "<ul>" + "".join(f"<li>{ic('check')}<span>{x}</span></li>" for x in items) + "</ul>"
    cards = (
        f'<div class="ins-card tilt" data-tilt="5" data-reveal><span class="icon-badge">{ic("shield")}</span><h3>In-Network PPO Plans</h3>'
        f'<p>Our front office works with dental plans regularly and can help you understand your benefits before treatment.</p>{lst(ppo)}</div>'
        f'<div class="ins-card tilt" data-tilt="5" data-reveal style="--d:.1s"><span class="icon-badge">{ic("smile")}</span><h3>In-House Savings Plan — $349/yr</h3>'
        f'<p>No insurance? Our plan costs less than $1 a day and less than regular insurance — with a wider range of savings.</p>{lst(plan)}</div>'
        f'<div class="ins-card tilt" data-tilt="5" data-reveal style="--d:.2s"><span class="icon-badge">{ic("card")}</span><h3>CareCredit Financing</h3>'
        f'<img class="cc-logo" src="assets/img/logo-carecredit.svg" alt="CareCredit" width="1106" height="150" loading="lazy">'
        f'<p>Spread the cost of larger treatment into manageable monthly payments.</p>{lst(cc)}</div>')
    pay = "".join(f"<span>{x}</span>" for x in ["Cash", "Checks", "Visa", "Mastercard", "American Express", "Discover", "CareCredit®"])
    lead = ("Cost should not keep you from addressing a dental concern early. We would rather take a few minutes to review your coverage than have uncertainty about cost delay the care you need."
            if page == "np" else
            "Pain shouldn’t have to wait on paperwork. Tell us your plan when you call and we’ll check your benefits — and if you don’t have insurance, the $349 in-house plan even includes an emergency exam.")
    return (f'<section class="insurance" id="insurance"><div class="bg" data-parallax><img src="assets/img/img-dental-insurance-and-financing-banner-phoenix.webp" alt="" loading="lazy" width="1600" height="1053"></div>'
            f'<div class="shell">{head_block("Insurance &amp; Financing", "Dental Insurance, Financing &amp; <em class=\"gold\">No-Insurance Options</em>", lead)}'
            f'{carousel(cards, "payment option", "m-carousel cols-3 ins-carousel", "ins-grid")}'
            f'<div class="pay-row" data-reveal><b>We accept</b>{pay}</div>'
            f'<div class="ins-callout" data-reveal>{ic("shield")}<p><strong>Not sure if we take your plan?</strong>Call {PHONE} — we’ll verify your benefits before treatment.</p>'
            f'<a class="btn btn-dark" {CALL} data-cta="insurance">{ic("phone", "ring-icon")}<span>Check My Insurance</span></a></div>'
            f'{section_cta(page, "insurance", "*CareCredit financing is subject to credit approval. Insurance coverage varies by plan.", dark=True)}</div></section>')


GALLERY = [  # the office's own photos (belmontdentistry.com/paradise-valley-az/office-tour/)
    ("img-belmont-dentistry-modern-reception-interior.webp", "Reception"),
    ("img-office-tour-living-area.webp", "Patient lounge"),
    ("img-belmont-dentistry-front-desk.webp", "Front desk"),
    ("img-belmont-dentistry-reception-area.webp", "Check-in"),
    ("img-belmont-dentistry-dental-treatment-room.webp", "Treatment room"),
    ("img-office-tour-dental-chair.webp", "Modern dental chairs"),
    ("img-belmont-dentistry-private-consultation-room.webp", "Private consultation room"),
    ("img-belmont-dentistry-office-conference-room.webp", "Treatment presentation space"),
    ("img-belmont-dentistry-dental-operatory.webp", "Operatory"),
    ("img-belmont-dentistry-clinical-workspace.webp", "Clinical workspace"),
]


def gallery_section(page, cls=""):
    shots = "".join(f'<figure class="shot"><img src="assets/img/{f}" alt="{PRACTICE} dental office — {c.lower()}" width="960" height="688" loading="lazy"><figcaption>{c}</figcaption></figure>'
                    for f, c in GALLERY)
    lead = ("A calm, spa-inspired office on N 40th St — with a coffee bar, the soft scent of lavender and modern technology in every room."
            if page == "np" else
            "A calm, modern office with digital X-rays and 3D CBCT imaging, so the cause of your pain is found quickly and treated right here.")
    return (f'<section class="section gallery {cls}" id="office"><div class="shell">{head_block("Office Tour", "Step Inside Our <em class=\"gold\">Paradise Valley Office</em>", lead)}'
            f'<div class="carousel" data-carousel data-auto data-reveal><div class="carousel-track">{shots}</div>'
            f'<div class="carousel-nav"><button class="carousel-btn" data-prev aria-label="Previous photo">{ic("left")}</button><div class="dots"></div><button class="carousel-btn" data-next aria-label="Next photo">{ic("right")}</button></div></div>'
            f'{section_cta(page, "gallery")}</div></section>')


def reviews_section(page, keys, cls=""):
    cards = "".join(review_card(k) for k in keys)
    title = "What Phoenix Patients <em class=\"gold\">Say About Us</em>" if page == "np" else "Real Patients. <em class=\"gold\">Real Relief.</em>"
    score = (f'<a class="score-card" href="{GMB_URL}" target="_blank" rel="noopener" data-cta="reviews-score">'
             f'<span class="big">{RATING}</span><div>{stars()}<small>{GOOGLE_G}{REVIEW_COUNT} Google reviews</small></div></a>')
    return (f'<section class="section {cls}" id="reviews"><div class="shell">'
            f'<div class="reviews-top"><div class="section-head" data-reveal><span class="kicker">Real Google Reviews</span><h2>{title}</h2>'
            f'<p>Unedited Google reviews from patients of our Paradise Valley office.</p></div><div data-reveal>{score}</div></div>'
            f'<div class="carousel" data-carousel data-auto data-reveal><div class="carousel-track">{cards}</div>'
            f'<div class="carousel-nav"><button class="carousel-btn" data-prev aria-label="Previous review">{ic("left")}</button><div class="dots"></div><button class="carousel-btn" data-next aria-label="Next review">{ic("right")}</button></div></div>'
            f'<div class="section-cta" data-reveal>'
            f'{btn_call(two("Call Now " + PHONE, "Call Now"), "btn btn-red btn-lg btn-pulse", "reviews") if page == "em" else btn_book(two("Book Your Visit Online", "Book Online"), "btn btn-gold btn-lg", "reviews")}'
            f'<a class="btn btn-outline btn-lg" href="{GMB_URL}" target="_blank" rel="noopener" data-cta="reviews">{ic("star")}<span>{two(f"Read All {REVIEW_COUNT} Reviews", "All Reviews")}</span></a></div>'
            f'</div></section>')


def faq_section(page, faqs):
    items = "".join(f'<details{" open" if i == 0 else ""}><summary>{q}{ic("down")}</summary><div class="answer"><p>{a}</p></div></details>'
                    for i, (q, a) in enumerate(faqs))
    title = "Frequently Asked <em class=\"gold\">Questions</em>"
    intro = ("Everything you need to know about our services, appointments, insurance, financing and patient care. Still have a question? Our team is happy to help."
             if page == "np" else
             "Quick answers for when something has gone wrong. If you are in pain right now, skip the reading — call us and we’ll take it from there.")
    if page == "em":
        cta = btn_call(f"Call Now {PHONE}", "btn btn-red btn-lg btn-pulse", "faq")
    else:
        cta = btn_book("Book Your Visit Online", "btn btn-gold btn-lg", "faq")
    return (f'<section class="section ink" id="faq"><div class="shell"><div class="faq-wrap">'
            f'<div class="faq-intro left" data-reveal="left"><span class="kicker">Questions</span><h2>{title}</h2><p>{intro}</p>{cta}'
            f'<p style="margin-top:18px"><a class="btn btn-ghost" {CALL if page == "np" else BOOK} data-cta="faq">'
            f'{ic("phone" if page == "np" else "calendar")}<span>{"Call " + PHONE if page == "np" else "Book Online"}</span></a></p></div>'
            f'<div class="faq-list" data-reveal="right">{items}</div></div></div></section>')


def short_hours(disp):
    """'7:30 am – 5:00 pm' -> '7:30am–5pm' so the week fits in a compact two-column grid."""
    s = disp.replace(":00", "").replace(" am", "am").replace(" pm", "pm").replace(" – ", "–")
    return s


def location_section(page):
    rows = "".join(f'<div class="h-row" data-day="{d}"><span>{label[:3]}{"*" if "*" in label else ""}</span><b>{short_hours(disp)}</b></div>'
                   for _, label, disp, d in HOURS)
    directions = (f'<a class="btn btn-gold btn-sm map-dir" href="{GMB_URL}" target="_blank" rel="noopener" data-cta="map-directions">'
                  f'{ic("nav")}<span>Get Directions</span></a>')
    if page == "ty":
        first = (f'<a class="btn btn-gold" href="{GMB_URL}" target="_blank" rel="noopener" data-cta="location-directions">'
                 f'{ic("nav")}<span>Directions</span></a>')
        second = btn_call("Call Us", "btn btn-ghost", "location")
    elif page == "em":
        first = btn_call("Call Now", "btn btn-red btn-pulse", "location")
        second = btn_book("Book Online", "btn btn-ghost", "location")
    else:
        first = btn_book("Book Online", "btn btn-gold", "location")
        second = btn_call("Call Us", "btn btn-ghost", "location")
    title = {"np": "Your Paradise Valley Dentist in <em class=\"gold\">North Phoenix</em>",
             "em": "Emergency Dentist Near <em class=\"gold\">Paradise Valley</em>",
             "ty": "Getting to <em class=\"gold\">Our Office</em>"}[page]
    lead = {"np": "Find us at 15255 N 40th St, Suite 141 — Floor 1 of Greenway Professional Park, convenient for Paradise Valley and North Phoenix families.",
            "em": "On N 40th St in Greenway Professional Park — an easy drive from Paradise Valley and across North Phoenix when you need care fast.",
            "ty": "We’re on Floor 1 of Greenway Professional Park, 15255 N 40th St. Look for Suite 141."}[page]
    return (f'<section class="section" id="location"><div class="shell">{head_block("Location &amp; Contact", title, lead)}'
            f'<div class="location-grid" data-reveal="zoom">'
            f'<div class="map"><div class="map-fallback"><div><p><strong>{PRACTICE}</strong><br>{ADDRESS}</p></div></div>'
            f'<iframe src="{MAP_EMBED}" title="Map to {PRACTICE}, {ADDRESS}" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe>{directions}</div>'
            f'<div class="contact-card"><div class="cc-head"><h3>{PRACTICE}</h3>{rating_pill("location-rating")}</div>'
            f'<div class="cc-info">'
            f'<a class="cc-item" href="{GMB_URL}" target="_blank" rel="noopener" data-cta="location-address">{ic("pin")}<span><strong>Address</strong>{STREET}, {CITY_LINE}<small>Floor 1 · Greenway Professional Park</small></span></a>'
            f'<a class="cc-item" {CALL} data-cta="location-phone">{ic("phone")}<span><strong>Call Us</strong>{PHONE}<small>Tap to call</small></span></a></div>'
            f'<div class="cc-hours"><div class="cc-hours-head"><strong>{ic("clock")}Office Hours</strong>'
            f'<span class="status" data-status><span class="live"></span><span class="label">Open Mon–Fri, 8 am–5 pm</span></span></div>'
            f'<div class="hours" role="table" aria-label="Office hours">{rows}</div><p class="hours-note">Book online any time, or call us during office hours.</p></div>'
            f'<div class="cc-btns">{first}{second}</div>'
            f'</div></div></div></section>')


def final_cta(page):
    if page == "em":
        h = "Don’t Wait Out <em class=\"gold\">the Pain.</em>"
        p = "Dental problems rarely get better on their own. Call now — we offer same-day emergency appointments to relieve pain quickly."
        btns = btn_call(f"Call Now {PHONE}", "btn btn-red btn-lg btn-pulse", "final") + btn_book("Book Online", "btn btn-ghost btn-lg", "final")
        chips = ["Same-day emergency visits", "New patients welcome", "In-network PPO plans"]
        img = "img-belmont-dentistry-dental-treatment-room.webp"
    else:
        h = "Start Your Smile Journey <em class=\"gold\">With Us.</em>"
        p = "New patients of all ages are welcome. Book an exam and cleaning online in under a minute, or call — our team will help you get started."
        btns = btn_book("Book Your Visit Online", "btn btn-gold btn-lg", "final") + btn_call(f"Call {PHONE}", "btn btn-ghost btn-lg", "final")
        chips = ["New patients welcome", "$349/yr in-house plan", "Spa-like comfort"]
        img = "img-belmont-dentistry-modern-reception-interior.webp"
    c = "".join(f"<li>{ic('check')}{x}</li>" for x in chips)
    return (f'<section class="final-cta"><div class="bg" data-parallax><img src="assets/img/{img}" alt="" loading="lazy" width="960" height="688"></div>'
            f'<div class="shell" data-reveal="zoom"><span class="kicker">{PRACTICE}</span><h2>{h}</h2><p>{p}</p>'
            f'<div class="btn-row">{btns}</div><ul class="chips">{c}</ul></div></section>')


def footer(page):
    return '<footer class="site-footer"><div class="shell"><p>© <span data-year>2026</span> Belmont Dentistry. All rights reserved.</p></div></footer>'


def sticky(page):
    if page == "ty":
        return (f'<div class="sticky-cta" role="region" aria-label="Quick contact">'
                f'<a class="btn btn-ghost" {CALL} data-cta="sticky">{ic("phone", "ring-icon")}<span>Call Us</span></a>'
                f'<a class="btn btn-gold" href="{GMB_URL}" target="_blank" rel="noopener" data-cta="sticky">{ic("nav")}<span>Directions</span></a></div>')
    if page == "em":
        return (f'<div class="sticky-cta" role="region" aria-label="Quick contact">'
                f'<a class="btn btn-red btn-pulse" {CALL} data-cta="sticky">{ic("phone", "ring-icon")}<span>Call Now</span></a>'
                f'<a class="btn btn-gold" {BOOK} data-cta="sticky">{ic("calendar")}<span>Book Online</span></a></div>')
    return (f'<div class="sticky-cta" role="region" aria-label="Quick contact">'
            f'<a class="btn btn-ghost" {CALL} data-cta="sticky">{ic("phone", "ring-icon")}<span>Call Us</span></a>'
            f'<a class="btn btn-gold" {BOOK} data-cta="sticky">{ic("calendar")}<span>Book Online</span></a></div>')


def usp_section(page, items_left, items_right, title, lead, img, cls="dark"):
    items = "".join(
        f'<div class="usp-item u{n + 1}{" r" if n >= 3 else ""}" data-reveal="{"right" if n >= 3 else "left"}" style="--d:{(n % 3) * .1:.1f}s">'
        f'<span class="usp-ico">{ic(icn)}</span><h3>{t}</h3><p>{s}</p></div>'
        for n, (icn, t, s) in enumerate(items_left + items_right))
    photo = (f'<div class="usp-photo tilt float" data-tilt="8" data-reveal="zoom"><img src="assets/img/{img}" '
             f'alt="The {PRACTICE} team" width="510" height="683" loading="lazy"></div>')
    return (f'<section class="section {cls}" id="why"><div class="shell">{head_block("Why Belmont Dentistry", title, lead)}'
            f'{carousel(photo + items, "reason", "m-carousel usp-carousel", "usp-grid")}'
            f'{section_cta(page, "why", dark=True)}</div></section>')


def offers_section(page, offers, perks, kicker, title, lead, cls="cream"):
    cards = []
    for i, (tag, big, small, text, cta_kind, cta_label, featured) in enumerate(offers):
        if cta_kind == "book":
            b = btn_book(cta_label, "btn btn-gold btn-block", "offer")
        else:
            b = btn_call(cta_label, "btn btn-red btn-block" if page == "em" else ("btn btn-gold btn-block" if featured else "btn btn-dark btn-block"), "offer")
        cards.append(f'<article class="offer tilt{" featured" if featured else ""}" data-tilt="6" data-reveal style="--d:{i * .1:.1f}s"><span class="tag">{tag}</span>'
                     f'<div class="big">{big}<small>{small}</small></div><p>{text}</p>{b}</article>')
    p = "".join(f"<li>{ic(icn)}{t}</li>" for icn, t in perks)
    return (f'<section class="section {cls}" id="offers"><div class="shell">{head_block(kicker, title, lead)}'
            f'<div class="carousel m-carousel cols-4" data-carousel><div class="carousel-track">{"".join(cards)}</div>'
            f'<div class="carousel-nav"><button class="carousel-btn" data-prev aria-label="Previous offer">{ic("left")}</button><div class="dots"></div><button class="carousel-btn" data-next aria-label="Next offer">{ic("right")}</button></div></div>'
            f'<ul class="perks" data-reveal>{p}</ul>{section_cta(page, "offers")}</div></section>')


def rating_coin():
    """3D spinning gold coin with the Google rating (desktop hero)."""
    face = (f'<span class="coin-face"><b>{RATING}</b>{stars()}<small>{REVIEW_COUNT} Google reviews</small></span>')
    return (f'<a class="coin" href="{GMB_URL}" target="_blank" rel="noopener" data-cta="hero-coin" aria-label="Rated {RATING} from {REVIEW_COUNT} Google reviews">'
            f'<span class="coin-spin">{face}<span class="coin-face coin-back">{GOOGLE_G}<small>Google Rating</small></span>'
            f'<span class="coin-edge"></span></span></a>')


SMILES = [  # real before/after cases shown on belmontdentistry.com/paradise-valley-az/
    ("img-porcelain-veneers-before-1.webp", "img-porcelain-veneers-after-1.webp", "Porcelain veneers"),
    ("img-teeth-whitening-before-1.webp", "img-teeth-whitening-after-1.webp", "Teeth whitening"),
    ("img-cosmetic-veneers-treatment-before-1.webp", "img-cosmetic-veneers-treatment-after-1.webp", "Cosmetic veneers"),
    ("img-in-office-teeth-whitening-before-1.webp", "img-in-office-teeth-whitening-after-1.webp", "In-office whitening"),
]


def smile_section(page):
    pairs = "".join(
        f'<figure class="ba" style="--pos:50%" data-reveal="flip">'
        f'<div class="ba-frame"><img src="assets/img/{a}" alt="{cap} — after treatment" width="468" height="275" loading="lazy">'
        f'<div class="ba-before"><img src="assets/img/{b}" alt="{cap} — before treatment" width="468" height="275" loading="lazy"></div>'
        f'<span class="ba-tag ba-tag-b">Before</span><span class="ba-tag ba-tag-a">After</span>'
        f'<span class="ba-handle" aria-hidden="true">{ic("left")}{ic("right")}</span>'
        f'<input class="ba-range" type="range" min="0" max="100" value="50" aria-label="Drag to compare before and after: {cap}"></div>'
        f'<figcaption>{cap}</figcaption></figure>'
        for b, a, cap in SMILES)
    steps = [("Discuss your smile goals", "We talk through what you’d like to change — color, shape, spacing or balance."),
             ("Evaluate your oral health", "Teeth, gums, bite and existing restorations are checked first."),
             ("Plan every phase", "You see the proposed direction before treatment begins."),
             ("Complete your transformation", "Whitening, veneers and bonding are completed in a logical order.")]
    sl = "".join(f'<li data-reveal style="--d:{i * .08:.2f}s"><span>0{i + 1}</span><div><strong>{h}</strong><p>{d}</p></div></li>' for i, (h, d) in enumerate(steps))
    return (f'<section class="section ink" id="smiles"><div class="shell">'
            f'{head_block("Smile Transformations", "Real Results From <em class=\"gold\">Our Patients</em>", "Drag the slider to compare real before-and-after cases — cosmetic and restorative results that show what careful planning can achieve.")}'
            f'<div class="smile-grid"><div>{carousel(pairs, "smile", "m-carousel cols-2 ba-carousel")}</div>'
            f'<div class="smile-copy" data-reveal="right"><h3>Your Smile Makeover, Planned Around You</h3>'
            f'<p>A smile makeover addresses several concerns at once — tooth color, shape, length and gum line are designed together, so nothing looks out of place.</p>'
            f'<ol class="smile-steps">{sl}</ol>'
            f'<div class="btn-row">{btn_book("Book a Smile Consultation", "btn btn-gold btn-lg", "smiles")}{btn_call(two(f"Call {PHONE}", "Call Us"), "btn btn-ghost btn-lg", "smiles")}</div>'
            f'</div></div></div></section>')


def hero_media(poster, video):
    return (f'<div class="hero-media"><img src="assets/img/{poster}" alt="" width="1280" height="720" fetchpriority="high">'
            f'<video data-lazy muted loop playsinline preload="none" poster="assets/img/{poster}" aria-hidden="true">'
            f'<source data-src="assets/video/{video}.webm" type="video/webm"><source data-src="assets/video/{video}.mp4" type="video/mp4"></video></div>'
            f'<img class="hero-watermark" src="assets/img/logo_watermark.svg" alt="" aria-hidden="true">'
            f'<button class="video-toggle" type="button" aria-label="Pause or play background video">{ic("pause", "i-pause")}{ic("play", "i-play")}</button>')


# --------------------------------------------------------------------------
# Structured data
# --------------------------------------------------------------------------
def schema(page, faqs, review_keys, url, desc):
    days = [{"@type": "OpeningHoursSpecification", "dayOfWeek": d, "opens": o, "closes": c} for d, o, c in [
        ("Monday", "08:00", "17:00"), ("Tuesday", "08:00", "17:00"), ("Wednesday", "08:00", "17:00"),
        ("Thursday", "08:00", "17:00"), ("Friday", "08:00", "17:00")]]
    reviews = [{"@type": "Review", "author": {"@type": "Person", "name": REVIEWS[k][0]},
                "reviewRating": {"@type": "Rating", "ratingValue": "5", "bestRating": "5"},
                "reviewBody": REVIEWS[k][2], "publisher": {"@type": "Organization", "name": "Google"}} for k in review_keys[:4]]
    dentist = {
        "@context": "https://schema.org", "@type": "Dentist", "@id": url + "#dentist",
        "name": PRACTICE, "description": desc, "url": url,
        "image": SITE + "/wp-content/uploads/2026/10/img-belmont-dentistry-modern-reception-interior.webp",
        "logo": SITE + "/wp-content/uploads/2026/10/cropped-img-Belmont-Dentistry-social-favicon.png",
        "telephone": "+1-480-530-3812", "priceRange": "$$", "hasMap": GMB_URL,
        "address": {"@type": "PostalAddress", "streetAddress": STREET, "addressLocality": "Phoenix",
                    "addressRegion": "AZ", "postalCode": "85032", "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": 33.6251, "longitude": -111.9945},
        "areaServed": ["Paradise Valley", "Phoenix", "North Phoenix"],
        "openingHoursSpecification": days,
        "aggregateRating": {"@type": "AggregateRating", "ratingValue": RATING, "reviewCount": REVIEW_COUNT, "bestRating": "5", "worstRating": "1"},
        "review": reviews,
        "employee": [{"@type": "Person", "name": full_name(n, s), "jobTitle": r} for n, s, r, *_ in DOCTORS],
        "paymentAccepted": "Cash, Check, Visa, Mastercard, American Express, Discover, CareCredit",
        "currenciesAccepted": "USD",
        "medicalSpecialty": "Dentistry",
        "availableService": [{"@type": "MedicalProcedure", "name": n} for n in (
            ["Emergency Dental Care", "Tooth Extraction", "Root Canal Therapy", "Dental Infection Treatment", "Crown and Filling Repair"] if page == "em"
            else ["Dental Cleanings and Exams", "Dental Implants", "Smile Makeover", "Porcelain Veneers", "Teeth Whitening", "Emergency Dental Care"])],
    }
    faq = {"@context": "https://schema.org", "@type": "FAQPage",
           "mainEntity": [{"@type": "Question", "name": re.sub(r"<[^>]+>", "", q),
                           "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a)}} for q, a in faqs]}
    return ('<script type="application/ld+json">' + json.dumps(dentist, ensure_ascii=False) + "</script>\n"
            '<script type="application/ld+json">' + json.dumps(faq, ensure_ascii=False) + "</script>")


def document(page, title, desc, slug, body, faqs, review_keys, theme="#1E1B16", robots="noindex, follow", head_extra=""):
    url = CANONICAL.get(slug, LP_BASE + slug + "/")
    ld = schema(page, faqs, review_keys, url, desc) if faqs else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
{head_extra}{GTM_HEAD}
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="{robots}">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="{theme}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Belmont Dentistry">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}/wp-content/uploads/2026/10/img-Belmont-Dentistry-social-1200x630-1.png">
<link rel="icon" href="assets/img/favicon-32.png" sizes="32x32">
<link rel="apple-touch-icon" href="assets/img/favicon-180.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Gloock&family=Karla:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/belmont.css">
<link rel="stylesheet" href="assets/css/pv-motion.css">
{ld}
</head>
<body data-page="{slug}" id="top">
{GTM_BODY}
<div class="scroll-progress" aria-hidden="true"><span></span></div>
{sprite()}
{body}
<script src="assets/js/lp.js" defer></script>
<script src="assets/js/pv-motion.js" defer></script>
</body>
</html>
"""


# ==========================================================================
# PAGE 1 — New patients / general dentist
# ==========================================================================
NP_FAQ = [
    ("Is Belmont Dentistry accepting new patients in Paradise Valley, AZ?",
     f"Yes. We welcome new patients of all ages and make the first visit simple. <a {BOOK}>Book an exam and cleaning online</a> or call {PHONE}, and our team will help you get started."),
    ("What dental services do you offer?",
     "Preventive care, restorative dentistry, cosmetic treatments, dental implants and emergency care — all in one office. That includes checkups and cleanings, fillings, crowns, veneers, whitening, smile makeovers, tooth replacement and extractions."),
    ("How often should I visit the dentist for a checkup and cleaning?",
     "Most patients should schedule an exam and professional cleaning every six months. Some people benefit from more frequent visits, such as those with gum disease or a higher risk of cavities — our doctors will recommend a schedule based on your oral health."),
    ("What dental insurance plans do you accept?",
     f"We’re in-network with several PPO plans and file claims for most others. Our front office team can verify your benefits before treatment, explain what your plan is expected to cover and help you plan around your annual maximum. Call {PHONE} to check your plan."),
    ("What if I don’t have dental insurance?",
     "You still have options. Our in-house savings plan is $349 a year and includes 2 check-ups, 1 emergency exam, 2 regular cleanings and all X-rays, plus 50% off Cone Beam CT scans and 20% off all services — with no claim forms. CareCredit financing is also available, subject to credit approval."),
    ("What happens at my first visit?",
     "Your first appointment begins in a calm, spa-inspired space with a coffee bar and the soft scent of lavender. We review your goals and concerns, take digital X-rays and intraoral images, show them to you on screen and discuss your options — and you leave with a hot towel to feel refreshed."),
    ("What should I bring to my first appointment?",
     "Please bring a photo ID, your dental insurance card if you have one, and a list of any medications you take. Complete your forms online ahead of time — they’re available in English and Spanish — so we can check you in almost instantly."),
    ("Do you offer dental implants and cosmetic dentistry?",
     "Yes. We replace missing teeth with dental implants and offer cosmetic options such as porcelain veneers, teeth whitening, bonding, gum recontouring and full smile makeovers. A consultation helps determine which treatments fit your goals and oral health."),
    ("What if I’m nervous about going to the dentist?",
     "Nitrous oxide, oral conscious sedation, noise-canceling headphones and soothing videos help patients stay relaxed and comfortable. We never rush you or press you into care you’re unsure about."),
    ("What are your office hours, and where are you located?",
     f"We’re at {ADDRESS}, on Floor 1 of Greenway Professional Park. We’re open Monday through Friday, 8:00 am to 5:00 pm. You can book online any time or call us during office hours."),
]

NP_REVIEWS = ["edgar", "hannah", "james", "kathleen", "lovell", "angelica", "michael", "medina"]


def page_new_patients():
    P = "np"
    hero = f"""
<section class="hero" id="hero">
  {hero_media("hero-poster-new-patients.webp", "hero-new-patients")}
  <div class="shell hero-grid">
    <div class="hero-copy">
      {rating_pill("hero-rating")}
      <p class="hero-eyebrow">Dentist in Paradise Valley, AZ <span class="dot"></span> New Patients Welcome</p>
      <h1 data-split>Exceptional Dental Care for <em>Paradise Valley Families.</em></h1>
      <p class="hero-lead">A privately owned Phoenix dental office where treatment decisions are made <strong>with you, not around quotas</strong> — in a calm, spa-like setting with a coffee bar, lavender and a hot towel. Nothing moves forward until you understand it and agree to it.</p>
      <div class="hero-ctas">
        {btn_book("Book Your Visit Online", "btn btn-gold btn-lg btn-shine", "hero")}
        {btn_call(f"Call {PHONE}", "btn btn-ghost btn-lg btn-pulse", "hero")}
      </div>
      <p class="hero-micro">Booking takes under a minute · No insurance? Ask about our <a href="#insurance">$349 in-house plan</a></p>
      <ul class="chips">
        <li>{ic("users")}New patients welcome</li>
        <li>{ic("shield")}In-network PPO plans</li>
        <li>{ic("clock")}Open Mon–Fri, 8–5</li>
        <li>{ic("coffee")}Spa-like comfort</li>
      </ul>
    </div>
    <aside class="hero-card" aria-label="New patient visit" data-reveal="right">
      {rating_coin()}
      <span class="card-badge">{ic("sparkles")}New Patients</span>
      <h2>Your First Visit, Made Easy</h2>
      <p class="sub">Here’s what every new patient gets at our Paradise Valley office:</p>
      <ul class="ticks">
        <li><span class="tick">{ic("check")}</span>A warm welcome in our comfortable reception lounge</li>
        <li><span class="tick">{ic("check")}</span>A real conversation about your dental history and concerns</li>
        <li><span class="tick">{ic("check")}</span>Digital X-rays and intraoral images reviewed with you on screen</li>
        <li><span class="tick">{ic("check")}</span>Your options explained — then a hot towel to leave refreshed</li>
      </ul>
      {btn_book("Book Online Now", "btn btn-gold btn-lg btn-block", "hero-card")}
      <p class="fine">Prefer to talk? <a {CALL} data-cta="hero-card">Call {PHONE}</a></p>
    </aside>
  </div>
  <span class="scroll-cue" aria-hidden="true"></span>
</section>"""

    st = stats([(f'<span data-count="{RATING}" data-decimals="1">{RATING}</span><span class="gold-text">★</span>', "Google rating"),
                (f'<span data-count="{REVIEW_COUNT}">{REVIEW_COUNT}</span>', "Google reviews"),
                ("2", "Experienced doctors"), ("Mon–Fri", "8 am – 5 pm")])

    offers = offers_section(P, [
        ("Members Save", "$349 a Year", "In-house savings plan",
         "Less than $1 a day: 2 check-ups, 1 emergency exam, 2 regular cleanings and all X-rays — plus 20% off all services.",
         "call", "Join the Plan", True),
        ("Insurance", "Free Benefits Check", "Before treatment begins",
         "In-network with several PPO plans and we file claims for most others — so you know what’s covered up front.",
         "call", "Check My Benefits", False),
        ("Technology", "50% Off CBCT", "For plan members",
         "Plan members save half on 3D Cone Beam CT scans — the detailed imaging used to plan implants with confidence.",
         "book", "Book Online", False),
        ("Financing", "Monthly Payments", "With CareCredit®",
         "Low or no interest options with qualifying approval — ideal for implants and smile makeovers.",
         "book", "Book Online", False),
    ], [("coffee", "Coffee bar"), ("sparkles", "Soft scent of lavender"), ("heart", "Hot towel service"),
        ("headphones", "Noise-canceling headphones"), ("monitor", "Soothing videos"), ("droplet", "Nitrous &amp; oral sedation")],
        "New Patient Offers", "Exceptional Care, <em class=\"gold\">Honest Pricing.</em>",
        "Cost shouldn’t keep you from addressing a dental concern early. Here’s how we make starting with a new dentist in Paradise Valley simple and affordable.")

    svc_cards = [
        ("img-preventive-care-phoenix-az.webp", "Preventive Care", "Comprehensive exams, cleanings and digital X-rays catch problems early."),
        ("img-dental-implants-phoenix-az.webp", "Dental Implants", "Natural-looking implants restore chewing strength and protect the jawbone."),
        ("img-smike-makeover-phoenix-az.webp", "Smile Makeover", "Personalized plans combining whitening, veneers and bonding for polished smiles."),
        ("img-emergency-care-phoenix-az.webp", "Emergency Care", "Prompt, compassionate care for toothaches, broken teeth and swelling."),
    ]
    svc = "".join(f'<a class="svc tilt" data-tilt="7" {BOOK} data-cta="service" data-reveal="flip" style="--d:{i * .1:.1f}s">'
                  f'<img src="assets/img/{f}" alt="{t} at {PRACTICE}" width="348" height="541" loading="lazy">'
                  f'<div class="svc-body"><h3>{t}</h3><p>{d}</p><span class="more">Book now {ic("arrow")}</span></div></a>'
                  for i, (f, t, d) in enumerate(svc_cards))
    svc_list = ["Checkups &amp; Cleanings", "Digital X-Rays", "Fillings", "Porcelain Crowns", "Dental Implants", "All-on-4 Implants",
                "Implant-Supported Dentures", "Tooth Extractions", "Porcelain Veneers", "Teeth Whitening", "Cosmetic Bonding", "Gum Recontouring",
                "Smile Makeovers", "Laser Dentistry", "Sedation Dentistry", "Emergency Care"]
    services = (f'<section class="section" id="services"><div class="shell">'
                f'{head_block("Comprehensive Dental Services", "Comprehensive Dental Services in <em class=\"gold\">Paradise Valley</em>", "Most dental needs can be handled right here by doctors who know your history — preventive, restorative, cosmetic, implant and emergency care in one location.")}'
                f'<div class="carousel m-carousel cols-4" data-carousel><div class="carousel-track">{svc}</div>'
                f'<div class="carousel-nav"><button class="carousel-btn" data-prev aria-label="Previous service">{ic("left")}</button><div class="dots"></div><button class="carousel-btn" data-next aria-label="Next service">{ic("right")}</button></div></div>'
                f'<ul class="svc-list" data-reveal>{"".join(f"<li>{ic("check")}{x}</li>" for x in svc_list)}</ul>'
                f'{section_cta(P, "services")}</div></section>')

    why = usp_section(P,
        [("award", "Crowns made to fit and look natural", "Porcelain crowns designed for a precise fit, a comfortable bite and a shade that blends in."),
         ("headphones", "Relaxing care for dental anxiety", "Nitrous oxide, oral conscious sedation, noise-canceling headphones and soothing videos."),
         ("scan", "Implants planned with digital imaging", "Detailed imaging evaluates bone and anatomy first, so you know whether implants are right for you.")],
        [("laser", "Comfortable laser dentistry", "Laser technology supports select soft-tissue procedures, often with less bleeding and easier healing."),
         ("clock", "Convenient weekday hours", "Open Monday through Friday, 8:00 am to 5:00 pm, with scheduling built around busy weekdays."),
         ("shield", "Insurance &amp; financing support", "Several in-network PPO plans, an in-house savings plan and CareCredit for larger treatment.")],
        "Why Phoenix Patients <em class=\"gold\">Choose Belmont Dentistry</em>",
        "A privately owned practice — not part of a corporate group — where appointments are scheduled to match what your mouth needs, not what the clock allows.",
        "img-Why-phoenix-Patients.webp")

    them = ["Treatment decisions made around quotas", "Appointments squeezed to fit the clock", "A quick verbal summary before moving on",
            "Pressure to say yes on the spot", "Dental anxiety tolerated, not addressed", "A cold, clinical waiting room", "Surprise costs discovered at checkout"]
    us = ["Treatment decisions made with you, never around quotas", "Appointments scheduled to match what your mouth needs", "Images shown on screen and options explained in plain language",
          "Nothing moves forward until you understand and agree", "Nitrous, oral sedation, headphones and soothing videos", "A spa-like visit — coffee bar, lavender &amp; a hot towel", "Benefits verified and costs reviewed before treatment"]
    us_col = f'<div class="compare-col us"><h3>Belmont Dentistry</h3><ul>{"".join(f"<li>{ic("check")}<span>{x}</span></li>" for x in us)}</ul></div>'
    them_col = f'<div class="compare-col them"><h3>A Typical Dental Office</h3><ul>{"".join(f"<li>{ic("x")}<span>{x}</span></li>" for x in them)}</ul></div>'
    compare = (f'<section class="section cream" id="difference"><div class="shell">'
               f'{head_block("The Belmont Difference", "A Phoenix Dental Office Built Around <em class=\"gold\">Patient Trust</em>", "We explain what we find, show you why it matters and outline your options in plain language before anything begins.")}'
               f'<div data-reveal="zoom">{carousel(us_col + them_col, "comparison", "m-carousel compare-carousel", "compare")}</div>'
               f'{section_cta(P, "compare")}</div></section>')

    visit = [("Book in under a minute", "Book an exam and cleaning online any time, or call us during office hours."),
             ("Fill out forms online", "Complete your forms ahead of time — in English or Spanish — and check in almost instantly."),
             ("Relax &amp; talk it through", "A warm welcome, a coffee bar and a real conversation about your goals and concerns."),
             ("See it on screen", "Digital X-rays and intraoral images reviewed with you, then your options explained clearly.")]
    vcards = "".join(f'<article class="step-card tilt" data-tilt="6" data-reveal="flip" style="--d:{i * .1:.1f}s"><h3>{h}</h3><p>{p}</p></article>' for i, (h, p) in enumerate(visit))
    bring = "".join(f"<li>{ic(i)}{t}</li>" for i, t in [("id", "Photo ID"), ("card", "Insurance card (if you have one)"), ("pill", "List of medications"), ("file", "Forms — online, in English or Spanish")])
    first_visit = (f'<section class="section cream" id="first-visit"><div class="shell">'
                   f'{head_block("Your First Visit", "What to Expect at <em class=\"gold\">Your First Visit</em>", "We never rush patients or press them into care they’re unsure about. We explain what we see, outline your choices and support whichever path you choose.")}'
                   f'<div class="carousel m-carousel cols-4 steps" data-carousel><div class="carousel-track">{vcards}</div>'
                   f'<div class="carousel-nav"><button class="carousel-btn" data-prev aria-label="Previous step">{ic("left")}</button><div class="dots"></div><button class="carousel-btn" data-next aria-label="Next step">{ic("right")}</button></div></div>'
                   f'<ul class="perks" data-reveal><li style="background:var(--brown);color:#fff;border-color:var(--brown)">What to bring:</li>{bring}</ul>'
                   f'{section_cta(P, "first-visit")}</div></section>')

    body = "\n".join([
        topbar(P), site_header(P), "<main>", hero, st, offers, services,
        marquee(["Open Monday–Friday 8–5", "In-Network PPO Plans", "$349/yr In-House Plan", "Family Owned, Not Corporate", "New Patients Welcome", f"{RATING}★ on Google"]),
        why, compare, doctors_section(P), awards_section(P), smile_section(P), insurance_section(P),
        reviews_section(P, NP_REVIEWS, "cream"), gallery_section(P), first_visit, faq_section(P, NP_FAQ), location_section(P), final_cta(P),
        "</main>", footer(P), sticky(P)])

    return document(
        P,
        "Dentist in Paradise Valley, AZ | Family Dentist | Belmont",
        f"Looking for a dentist in Paradise Valley, AZ? Belmont Dentistry welcomes new patients in North Phoenix. {RATING}★ on Google, PPO plans & a $349/yr plan. Book online.",
        "new-patients-paradise-valley", body, NP_FAQ, NP_REVIEWS)


# ==========================================================================
# PAGE 2 — Emergency dentist
# ==========================================================================
EM_FAQ = [
    ("Do you offer same-day emergency appointments in Paradise Valley?",
     f"Yes. We offer same-day emergency appointments for severe toothaches, broken or knocked-out teeth, lost fillings and swelling. Call {PHONE} as soon as the problem starts so our team can arrange care and relieve pain quickly."),
    ("What qualifies as a dental emergency?",
     "Severe tooth pain, significant swelling, dental infections, knocked-out teeth, broken or severely cracked teeth, uncontrolled bleeding and damaged dental restorations may need urgent attention. If you’re unsure how serious it is, call us for guidance."),
    ("Do you do emergency tooth extractions?",
     "Yes. When a tooth is too damaged, infected or broken to be saved, it can be removed here. The area is numbed with local anesthesia first, the procedure is explained before it begins, and you leave with clear recovery instructions."),
    ("What should I do if I have severe tooth pain?",
     "Call us for an evaluation rather than waiting for the pain to disappear on its own. Avoid chewing on the painful side and don’t place aspirin directly against your gums or tooth — it can irritate the soft tissue."),
    ("What should I do if my tooth is knocked out?",
     "Handle the tooth only by the crown and avoid touching the root. Keep it moist and bring it with you as quickly as possible — prompt dental attention may improve the chance of preserving the tooth."),
    ("Can a broken tooth be treated during an emergency visit?",
     "Treatment depends on the extent and location of the damage. We may be able to provide immediate care to protect the tooth and relieve discomfort, with bonding, a crown or root canal therapy recommended if needed."),
    ("What should I do if my dental crown falls out?",
     "Keep the crown and bring it with you. Avoid chewing on the exposed tooth and call us promptly — the crown may be repaired or replaced, depending on its condition and the health of the tooth underneath."),
    ("Does a dental infection always cause severe pain?",
     "No. An infection can develop with mild symptoms or without significant pain, especially early on. Swelling, tenderness, pressure, an unpleasant taste or changes around a tooth should also be evaluated."),
    ("I don’t have insurance. What will an emergency visit cost?",
     "We’ll explain costs before treatment. Our $349-a-year in-house savings plan includes an emergency exam and all X-rays, and CareCredit can spread larger treatment into monthly payments, subject to credit approval."),
    ("When are you open?",
     f"Monday through Friday, 8:00 am to 5:00 pm, at {ADDRESS}. Call {PHONE} as soon as symptoms start so we can see you the same day."),
]

EM_REVIEWS = ["angelica", "james", "hannah", "kathleen", "michael", "lovell", "edgar", "terri"]


def page_emergency():
    P = "em"
    triage = [("flame", "Severe toothache"), ("broken", "Broken / cracked tooth"), ("droplet", "Swelling or infection"), ("tooth", "Lost filling or crown"),
              ("alert", "Knocked-out tooth"), ("zap", "Tooth extraction"), ("smile", "Dental trauma"), ("heart", "Gum swelling")]
    tri = "".join(f'<a {CALL} data-cta="triage">{ic(i)}<span>{t}</span></a>' for i, t in triage)
    hero = f"""
<section class="hero hero-emergency" id="hero">
  {hero_media("hero-poster-emergency.webp", "hero-emergency")}
  <div class="shell hero-grid">
    <div class="hero-copy">
      <div style="display:flex;flex-wrap:wrap;gap:10px;justify-content:inherit">{rating_pill("hero-rating")}<span class="status" data-status><span class="live"></span><span class="label">Same-day emergency appointments</span></span></div>
      <p class="hero-eyebrow">Same-Day Emergency Dental Care <span class="dot"></span> Paradise Valley, AZ</p>
      <h1 data-split>Emergency Dentist in Paradise Valley. <em>Same-Day Relief.</em></h1>
      <p class="hero-lead">Severe toothache, a broken or knocked-out tooth, a lost filling or swelling? We offer <strong>same-day emergency appointments</strong> — call as soon as the problem starts so our team can arrange care and relieve your pain quickly.</p>
      <div class="hero-ctas">
        {btn_call(f"Call Now {PHONE}", "btn btn-red btn-lg btn-pulse", "hero")}
        {btn_book("Book Online", "btn btn-ghost btn-lg", "hero")}
      </div>
      <p class="hero-micro">Calling is the fastest way in — new patients are always welcome.</p>
      <ul class="chips">
        <li>{ic("zap")}Same-day appointments</li>
        <li>{ic("tooth")}Emergency extractions</li>
        <li>{ic("users")}New patients welcome</li>
        <li>{ic("clock")}Mon–Fri, 8–5</li>
      </ul>
    </div>
    <aside class="hero-card" aria-label="Tell us what's wrong" data-reveal="right">
      {rating_coin()}
      <span class="card-badge red">{ic("siren")}Fast Pain Relief</span>
      <h2>What’s Going On?</h2>
      <p class="sub">Tap your problem to call our Paradise Valley team directly.</p>
      <div class="triage">{tri}</div>
      {btn_call(f"Call {PHONE}", "btn btn-red btn-lg btn-block btn-pulse", "hero-card")}
      <p class="fine">or <a {BOOK} data-cta="hero-card">book online</a> — same-day slots when available</p>
    </aside>
  </div>
  <span class="scroll-cue" aria-hidden="true"></span>
</section>"""

    st = stats([("Same Day", "Emergency visits"), (f'<span data-count="{RATING}" data-decimals="1">{RATING}</span><span class="gold-text">★</span>', f"{REVIEW_COUNT} Google reviews"),
                ("Mon–Fri", "8 am – 5 pm"), ("All Ages", "Kids, adults &amp; seniors")])

    conds = [
        ("flame", "Severe Toothache", "Pain that interferes with eating, sleeping or normal activities needs prompt evaluation.", ""),
        ("droplet", "Dental Infection", "Swelling, tenderness, pressure or an abscess may mean an infection that needs treatment.", "Urgent"),
        ("broken", "Broken or Cracked Tooth", "Trauma, biting forces or weakened structure can chip, crack or break a tooth.", ""),
        ("alert", "Knocked-Out Tooth", "A completely displaced tooth needs immediate attention — keep it moist and call.", "Minutes matter"),
        ("tooth", "Lost Filling", "A missing filling leaves the tooth exposed and vulnerable to sensitivity or damage.", ""),
        ("shield", "Loose or Damaged Crown", "A displaced restoration exposes the tooth underneath — bring the crown with you.", ""),
        ("heart", "Gum or Facial Swelling", "Sudden swelling may be linked to an infection or another dental concern.", ""),
        ("zap", "Emergency Tooth Extraction", "When a tooth can’t be saved, we remove it comfortably after thorough numbing.", ""),
    ]
    cc = "".join(f'<article class="cond tilt" data-tilt="6" data-reveal="flip" style="--d:{(i % 4) * .08:.2f}s">'
                 f'{f"<span class=urgent-tag>{u}</span>" if u else ""}<span class="icon-badge red">{ic(icn)}</span><h3>{t}</h3><p>{d}</p>'
                 f'<a class="call-link" {CALL} data-cta="condition">{ic("phone")}Call about this</a></article>'
                 for i, (icn, t, d, u) in enumerate(conds))
    conditions = (f'<section class="section" id="emergencies"><div class="shell">'
                  f'{head_block("Dental Emergencies We Treat", "Prompt Care for <em class=\"gold\">Unexpected Dental Problems</em>", "Some emergencies involve sudden pain, others visible damage without much discomfort. If something feels wrong, call — we’ll tell you what to do next.")}'
                  f'<div class="carousel m-carousel cols-4" data-carousel><div class="carousel-track">{cc}</div>'
                  f'<div class="carousel-nav"><button class="carousel-btn" data-prev aria-label="Previous">{ic("left")}</button><div class="dots"></div><button class="carousel-btn" data-next aria-label="Next">{ic("right")}</button></div></div>'
                  f'{section_cta(P, "conditions")}</div></section>')

    aid = [
        ("alert", "Knocked-out tooth", "Pick it up by the crown, not the root. Keep it moist, don’t scrub it, and bring it with you."),
        ("broken", "Broken tooth", "Save any broken pieces and bring them along. Avoid chewing on that side until it’s checked."),
        ("droplet", "Swelling", "Call us promptly. A cold compress on the outside may help — never apply heat to the area."),
        ("tooth", "Lost filling or crown", "Keep the restoration if you have it and avoid chewing on the exposed tooth."),
        ("flame", "Severe toothache", "Don’t place aspirin against the tooth or gums — it irritates the tissue. Call us for guidance."),
        ("snow", "Dental trauma", "After an accident or injury to the mouth, call right away so we can examine it urgently."),
    ]
    ac = "".join(f'<article class="aid tilt" data-tilt="5" data-reveal="flip" style="--d:{(i % 3) * .1:.1f}s"><h3>{ic(icn)}{t}</h3><p>{d}</p></article>' for i, (icn, t, d) in enumerate(aid))
    first_aid = (f'<section class="section cream" id="first-aid"><div class="shell">'
                 f'{head_block("Before You Reach the Office", "What to Do <em class=\"gold\">Right Now</em>", "Knowing how to respond can help protect the affected area until you receive professional care.")}'
                 f'<div class="carousel m-carousel cols-3" data-carousel><div class="carousel-track">{ac}</div>'
                 f'<div class="carousel-nav"><button class="carousel-btn" data-prev aria-label="Previous tip">{ic("left")}</button><div class="dots"></div><button class="carousel-btn" data-next aria-label="Next tip">{ic("right")}</button></div></div>'
                 f'{section_cta(P, "first-aid")}</div></section>')

    tx = [("Emergency tooth extraction", "When a tooth can’t be saved — thoroughly numbed, with clear recovery guidance."),
          ("Root canal therapy", "Treats the infection behind throbbing pain and helps preserve the tooth."),
          ("Infection treatment", "Swelling, pressure or an abscess evaluated and treated before it spreads."),
          ("Broken &amp; cracked teeth", "Immediate care to protect the tooth, then bonding or a crown if needed."),
          ("Lost fillings &amp; loose crowns", "Restorations repaired or replaced to stop sensitivity and further damage."),
          ("Dental trauma", "Injuries to the teeth, gums or mouth examined and treated urgently.")]
    tlist = "".join(f'<li><span class="tick">{ic("check")}</span><div><strong>{t}</strong><span>{d}</span></div></li>' for t, d in tx)
    treatments = (f'<section class="section ink" id="services"><div class="shell"><div class="split">'
                  f'<div class="split-copy left" data-reveal="left"><span class="kicker">Emergency Treatment</span>'
                  f'<h2>We Don’t Just Numb It. <em class="gold">We Fix It.</em></h2>'
                  f'<p>Emergency visits focus on finding what’s causing the problem and the right next step — treating an infection, repairing a damaged tooth, relieving pain or restoring a broken restoration.</p>'
                  f'<ul class="checklist">{tlist}</ul>'
                  f'<div class="btn-row">{btn_call(f"Call Now {PHONE}", "btn btn-red btn-lg btn-pulse", "treatments")}{btn_book("Book Online", "btn btn-ghost btn-lg", "treatments")}</div></div>'
                  f'<div class="split-media tilt img-reveal" data-tilt="6" data-reveal="right"><img src="assets/img/img-office-tour-dental-chair.webp" alt="Treatment room at {PRACTICE}" width="960" height="640" loading="lazy">'
                  f'<span class="media-badge">{ic("zap")}Same-day emergency appointments</span></div></div></div></section>')

    proc = [("We listen to what happened", "Explain your symptoms, when they began and whether an injury caused the problem."),
            ("The area is evaluated", "Your tooth, gums and surrounding areas are checked for damage, infection or inflammation."),
            ("Imaging if needed", "Digital X-rays reveal problems beneath the surface, like infection or hidden damage."),
            ("Options explained", "We discuss the recommended treatment with you before anything begins."),
            ("Immediate care", "When it’s safe to start, we address the concern, protect the tooth and ease your pain."),
            ("Next steps planned", "If more treatment is needed, we explain what has to happen next and why.")]
    pc = "".join(f'<article class="step-card tilt" data-tilt="6" data-reveal="flip" style="--d:{(i % 3) * .1:.1f}s"><h3>{h}</h3><p>{p}</p></article>' for i, (h, p) in enumerate(proc))
    process = (f'<section class="section" id="process"><div class="shell">'
               f'{head_block("Your Emergency Visit", "What to Expect During <em class=\"gold\">Emergency Care</em>", "We focus first on understanding the problem and what needs attention — the exact treatment depends on the nature and severity of the emergency.")}'
               f'<div class="carousel m-carousel cols-3 steps" data-carousel data-auto><div class="carousel-track">{pc}</div>'
               f'<div class="carousel-nav"><button class="carousel-btn" data-prev aria-label="Previous step">{ic("left")}</button><div class="dots"></div><button class="carousel-btn" data-next aria-label="Next step">{ic("right")}</button></div></div>'
               f'{section_cta(P, "process")}</div></section>')

    why = usp_section(P,
        [("zap", "Same-day appointments", "Call as soon as the problem starts and we’ll arrange care to relieve your pain quickly."),
         ("clock", "Convenient weekday hours", "Open Monday through Friday, 8:00 am to 5:00 pm."),
         ("tooth", "Most treatment in-house", "Extractions, root canals, infection care and crown repairs — handled right here.")],
        [("scan", "Answers you can see", "Digital X-rays and 3D CBCT imaging show what’s wrong, explained in plain language."),
         ("headphones", "Relaxing care", "Nitrous oxide, oral conscious sedation, noise-canceling headphones and soothing videos."),
         ("shield", "Costs before treatment", "In-network PPO plans, a $349/yr in-house plan and CareCredit financing.")],
        "Why Phoenix Calls Belmont <em class=\"gold\">First</em>",
        "A privately owned practice with two experienced doctors and the technology to diagnose and treat most dental emergencies in one visit.",
        "img-Why-phoenix-Patients.webp")

    offers = offers_section(P, [
        ("Fast Access", "Same-Day Emergency Visits", "New patients welcome",
         "Call as soon as symptoms start — our team arranges care the same day to relieve your pain quickly.",
         "call", "Call Now", True),
        ("No Insurance?", "$349 a Year", "Includes an emergency exam",
         "Our in-house plan covers 1 emergency exam and all X-rays, plus 2 check-ups, 2 cleanings and 20% off all services.",
         "call", "Ask About the Plan", False),
        ("Insurance", "Free Benefits Check", "In-network PPO plans",
         "We’re in-network with several PPO plans and file claims for most others — costs explained before treatment.",
         "call", "Check My Insurance", False),
        ("Financing", "Pay Over Time", "With CareCredit®",
         "Don’t let cost delay urgent care — low or no interest options with qualifying approval.",
         "book", "Book Online", False),
    ], [("droplet", "Nitrous oxide"), ("pill", "Oral conscious sedation"), ("headphones", "Noise-canceling headphones"),
        ("monitor", "Soothing videos"), ("coffee", "Coffee bar"), ("child", "Patients of all ages")],
        "Emergency Care Made Easy", "In Pain? No Insurance? <em class=\"gold\">We’ve Got You.</em>",
        "Getting out of pain shouldn’t be complicated. Here’s how we make emergency dental care in Paradise Valley fast, comfortable and affordable.")

    body = "\n".join([
        topbar(P), site_header(P), "<main>", hero, st, conditions,
        marquee(["Same-Day Emergency Appointments", "Emergency Tooth Extraction", "Root Canal Therapy", "Infection Treatment", "In-Network PPO Plans", "Open Mon–Fri 8–5"], red=True),
        first_aid, treatments, process, reviews_section(P, EM_REVIEWS, "cream"), why, offers, doctors_section(P),
        awards_section(P), insurance_section(P), gallery_section(P, "cream"), faq_section(P, EM_FAQ), location_section(P), final_cta(P),
        "</main>", footer(P), sticky(P)])

    return document(
        P,
        "Paradise Valley Emergency Dentist | Same-Day Care | Belmont",
        f"Need an emergency dentist in Paradise Valley or North Phoenix? Same-day emergency appointments for toothaches & broken teeth. {RATING}★ on Google. Call {PHONE}.",
        "emergency-dentist-paradise-valley", body, EM_FAQ, EM_REVIEWS, theme="#1E1B16")


# ==========================================================================
# PAGE 3 — Thank-you page (shared by both landing pages)
# ==========================================================================
# Fires before GTM loads, so a "Custom Event = thank_you_view" trigger can
# record the booking conversion. lp_source says which landing page sent the
# visitor (?from=emergency|new-patients, or the referrer when present).
TY_DATALAYER = """<script>
window.dataLayer = window.dataLayer || [];
(function () {
  var q = new URLSearchParams(location.search), r = document.referrer || '';
  var src = q.get('from') || (r.indexOf('emergency') > -1 ? 'emergency' : r.indexOf('new-patients') > -1 ? 'new-patients' : 'direct');
  window.dataLayer.push({ event: 'thank_you_view', lp_page: 'thank-you-paradise-valley', lp_source: src });
})();
</script>
"""


def page_thank_you():
    P = "ty"
    hero = f"""
<section class="hero ty-hero" id="hero">
  <div class="hero-media"><img src="assets/img/img-belmont-dentistry-modern-reception-interior.webp" alt="" width="960" height="688" fetchpriority="high"></div>
  <img class="hero-watermark" src="assets/img/logo_watermark.svg" alt="" aria-hidden="true">
  <div class="shell">
    <div class="ty-check" aria-hidden="true"><svg viewBox="0 0 52 52"><circle cx="26" cy="26" r="24"/><path d="M15 27l7 7 15-16"/></svg></div>
    <p class="hero-eyebrow">Belmont Dentistry Paradise Valley <span class="dot"></span> Request Received</p>
    <h1>Thank You! <em>We’ll See You Soon.</em></h1>
    <p class="hero-lead">Your request has been sent to our Paradise Valley team. You’ll get a confirmation by text or email shortly — and if anything needs a quick check, we’ll call you from <strong>{PHONE}</strong>.</p>
    <div class="hero-ctas">
      <a class="btn btn-gold btn-lg" href="#next-steps" data-cta="hero">{ic("check")}<span>See What Happens Next</span></a>
      {btn_call(f"Call {PHONE}", "btn btn-ghost btn-lg", "hero")}
    </div>
    <div class="ty-trust">{rating_pill("hero-rating")}</div>
  </div>
</section>"""

    steps = [
        ("calendar", "Watch for your confirmation", f"Your appointment details arrive by text or email. Don’t see them within a few minutes? Check spam, or call us at {PHONE}.", ""),
        ("file", "Fill out your forms online", "Save time at check-in by completing your new patient forms before your visit — it only takes a few minutes.",
         f'<a class="btn btn-dark btn-block" href="{SITE}/paradise-valley-az/patient-forms/" target="_blank" rel="noopener" data-cta="forms">{ic("file")}<span>Patient Forms</span></a>'),
        ("clock", "Arrive 10 minutes early", "A few extra minutes lets us check you in, confirm your insurance and get you settled with a blanket and headphones.",
         f'<a class="btn btn-outline btn-block" href="{GMB_URL}" target="_blank" rel="noopener" data-cta="steps-directions">{ic("nav")}<span>Get Directions</span></a>'),
    ]
    sc = "".join(f'<article class="step-card tilt" data-tilt="6" data-reveal style="--d:{i * .1:.1f}s"><h3>{h}</h3><p>{d}</p>{b}</article>'
                 for i, (_, h, d, b) in enumerate(steps))
    bring = "".join(f"<li>{ic(i)}{t}</li>" for i, t in [("id", "Photo ID"), ("card", "Insurance card (if you have one)"), ("pill", "List of current medications"), ("file", "Previous X-rays (optional)")])
    next_steps = (f'<section class="section cream" id="next-steps"><div class="shell">'
                  f'{head_block("What Happens Next", "Three Easy Steps <em class=\"gold\">Before Your Visit</em>", "A little preparation makes your first visit quick, comfortable and stress-free.")}'
                  f'<div class="carousel m-carousel cols-3 steps" data-carousel><div class="carousel-track">{sc}</div>'
                  f'<div class="carousel-nav"><button class="carousel-btn" data-prev aria-label="Previous step">{ic("left")}</button><div class="dots"></div><button class="carousel-btn" data-next aria-label="Next step">{ic("right")}</button></div></div>'
                  f'<ul class="perks" data-reveal><li style="background:var(--brown);color:#fff;border-color:var(--brown)">What to bring:</li>{bring}</ul>'
                  f'<div class="er-warning ty-help" data-reveal>{ic("siren")}<p><strong>Need to reschedule, or in pain before your appointment?</strong> Call {PHONE} — we offer same-day emergency appointments.</p>'
                  f'<a class="btn btn-red btn-pulse" {CALL} data-cta="ty-help">{ic("phone", "ring-icon")}<span>Call Now</span></a></div>'
                  f'</div></section>')

    team = "".join(f'<article class="team-mini" data-reveal style="--d:{i * .1:.1f}s"><img src="{img}" alt="{full_name(n, s)}" width="467" height="611" loading="lazy">'
                   f'<h3>{full_name(n, s)}</h3><span>{r} · {c.split(" · ")[-1] if c.startswith("DDS") else c.split(" · ")[0]}</span></article>'
                   for i, (n, s, r, c, img, *_rest) in enumerate(DOCTORS))
    comfort = "".join(f"<li>{ic(i)}{t}</li>" for i, t in [("headphones", "Noise-cancelling headphones"), ("monitor", "TVs in every room"), ("blanket", "Warm blankets"),
                                                         ("coffee", "Complimentary beverages"), ("droplet", "Nitrous &amp; oral sedation"), ("heart", "A team that listens")])
    dentists = (f'<section class="section ink" id="dentists"><div class="shell">'
                f'{head_block("You’re in Good Hands", "Meet the Team <em class=\"gold\">Caring for You</em>", f"A privately owned practice rated {RATING}★ by {REVIEW_COUNT} Google reviewers. Here’s who you’ll meet.")}'
                f'<div class="team-grid">{team}</div>'
                f'<h3 class="ty-sub" data-reveal>Your comfort menu — included at every visit</h3><ul class="perks dark" data-reveal>{comfort}</ul>'
                f'<div class="section-cta" data-reveal><a class="btn btn-gold btn-lg" href="{GMB_URL}" target="_blank" rel="noopener" data-cta="dentists">{ic("star")}<span>{two(f"Read Our {REVIEW_COUNT} Reviews", "Our Reviews")}</span></a>'
                f'{btn_call(two(f"Call {PHONE}", "Call Us"), "btn btn-ghost btn-lg", "dentists")}</div></div></section>')

    body = "\n".join([site_header(P), "<main>", hero, next_steps, dentists, location_section(P), "</main>", footer(P), sticky(P)])
    return document(
        P,
        "Thank You | Belmont Dentistry Paradise Valley",
        "Thank you for choosing Belmont Dentistry Paradise Valley. Here’s what happens next, what to bring and how to find our office at 15255 N 40th St, STE 141.",
        "thank-you-paradise-valley", body, None, None, robots="noindex, nofollow", head_extra=TY_DATALAYER)


# ==========================================================================
# Standalone (single-file) copies
# ==========================================================================
VIDEO_BASE_STANDALONE = "assets/video/"   # change to an absolute URL once the videos are uploaded


def bundle(src: Path, out: Path):
    text = src.read_text(encoding="utf-8")

    def data_uri(rel):
        p = HERE / rel
        mime = mimetypes.guess_type(str(p))[0] or "application/octet-stream"
        if p.suffix == ".svg":
            mime = "image/svg+xml"
        elif p.suffix == ".webp":
            mime = "image/webp"
        return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode("ascii")

    text = re.sub(r'<link rel="stylesheet" href="(assets/css/[^"]+)">',
                  lambda m: "<style>\n" + (HERE / m.group(1)).read_text(encoding="utf-8") + "\n</style>", text)
    text = re.sub(r'<script src="(assets/js/[^"]+)" defer></script>',
                  lambda m: "<script>\n" + (HERE / m.group(1)).read_text(encoding="utf-8") + "\n</script>", text)
    text = re.sub(r'(src|href|poster)="(assets/img/[^"]+)"', lambda m: f'{m.group(1)}="{data_uri(m.group(2))}"', text)
    text = text.replace('data-src="assets/video/', f'data-src="{VIDEO_BASE_STANDALONE}')
    out.write_text(text, encoding="utf-8")
    return out.stat().st_size


def main():
    pages = {
        "new-patients-paradise-valley.html": page_new_patients(),
        "emergency-dentist-paradise-valley.html": page_emergency(),
        "thank-you-paradise-valley.html": page_thank_you(),
    }
    (HERE / "standalone").mkdir(exist_ok=True)
    for name, doc in pages.items():
        (HERE / name).write_text(doc, encoding="utf-8")
        size = bundle(HERE / name, HERE / "standalone" / name)
        print(f"wrote {name} ({len(doc) / 1024:.0f} KB) + standalone/{name} ({size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
