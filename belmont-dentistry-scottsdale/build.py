#!/usr/bin/env python3
"""
Build the two Belmont Dentistry Scottsdale Google Ads landing pages.

    new-patients-scottsdale.html        (new patient / general dentist)
    emergency-dentist-scottsdale.html   (emergency dentist)

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
# Practice facts — Scottsdale office only
# --------------------------------------------------------------------------
PHONE = "(480) 602-8050"
TEL = "tel:+14806028050"
BOOK_URL = "https://book.allinone.dental/belmont-scottsdale?referrer_id=4"
GMB_URL = "https://maps.app.goo.gl/AYHuqmcoSysNogFbA"
MAP_EMBED = ("https://www.google.com/maps/embed?pb=!1m14!1m8!1m3!1d26578.880977977937!2d-111.89563452720998"
             "!3d33.62190335198103!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x872b75b3e14d4c53%3A0xd82d6ff38791f364"
             "!2sBelmont%20Dentistry%20Scottsdale!5e0!3m2!1sen!2sus!4v1790597629590!5m2!1sen!2sus")
STREET = "8350 E Raintree Dr, Suite 115"
CITY_LINE = "Scottsdale, AZ 85260"
ADDRESS = f"{STREET}, {CITY_LINE}"
RATING = "4.9"
REVIEW_COUNT = "699"          # Google, Scottsdale listing — read Oct 2026
SITE = "https://www.belmontdentistry.com"
LP_BASE = SITE + "/lp/"

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

HOURS = [  # (schema day, label, display, js day index)
    ("Monday", "Monday", "7:00 am – 5:00 pm", 1),
    ("Tuesday", "Tuesday", "7:00 am – 6:00 pm", 2),
    ("Wednesday", "Wednesday", "7:00 am – 5:00 pm", 3),
    ("Thursday", "Thursday", "7:00 am – 6:00 pm", 4),
    ("Friday", "Friday*", "8:00 am – 3:00 pm", 5),
    ("Saturday", "Saturday*", "8:00 am – 2:00 pm", 6),
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
# Real Google reviews of the Scottsdale office (verbatim, from the site's
# Google review feed, Oct 2026). Spelling kept as written by the patient.
# --------------------------------------------------------------------------
REVIEWS = {
    "lisa": ("Lisa Weisman", "Emergency visit",
             "We were here from out of town when my daughter got an infection and abscess. She was in extreme pain and over the counter and home remedies weren’t working. I searched for “emergency dentist near me” and called Belmont - they got us in within 2 hours of my call. Extremely helpful and friendly and had her with an antibiotic to get her home in no time. So grateful for the friendly service!"),
    "kaci": ("kaci manzanedo", "Dental anxiety",
             "The people are wonderful. I have a deep deep fear of the dentist from past dental trauma and these people were kind, professional and compassionate."),
    "liann": ("LiAnn Seale", "Patient since 2021",
              "After moving across the country in 2021, I was so stressed to find a good dentist. Luckily, Belmont was the first one I found. And I’m so grateful I did! They’ve taken care of my cleanings, some fillings, and even a cracked front tooth. Everyone is so kind and attentive, from the front desk, hygienists, to the dentists. They explain things in detail, make you feel comfortable, and ease any dental anxiety you may have. This place is a gem."),
    "art": ("Art Powell", "New patient",
            "First time at this office and they were ready when I walked in. Cleaning was good, she did a great job. Very detailed. Only had to wait two days for an appointment. Today I had treatment and Adrianna and Dr. Hong were great 😃."),
    "wyn": ("Wyn Harrison", "Second opinion",
            "The office was welcoming and efficient. Dr. Hong provided a thoughtful, conservative second opinion. She then effectively treated the problem. Thank you for excellent dental care."),
    "jennifer": ("Jennifer McConnell", "Family care",
                 "Great neighborhood dental team that is knowledgeable, friendly and genuinely cares for their patients."),
    "susan": ("Susan Klocke", "On-time care",
              "They were very good, right on time with appointments, made me feel at ease."),
    "estela": ("Estela Simental", "Fast & affordable",
               "It was really fast, very Confortable, Staff very Nice , profesional and Overall the prices really good."),
}


def review_card(key):
    name, tag, text = REVIEWS[key]
    initials = "".join(w[0] for w in name.split()[:2]).upper()
    return (f'<figure class="review"><span class="quote-mark" aria-hidden="true">“</span>{stars()}'
            f'<span class="tagline">{tag}</span><blockquote>{text}</blockquote>'
            f'<footer><span class="avatar" aria-hidden="true">{initials}</span><div><strong>{name}</strong>'
            f'<small>{GOOGLE_G} Google review · Scottsdale</small></div></footer></figure>')


# --------------------------------------------------------------------------
# Shared sections
# --------------------------------------------------------------------------
def topbar(page):
    if page == "em":
        return (f'<div class="topbar urgent"><div class="shell"><a {CALL} data-cta="topbar">{ic("siren")}'
                f'Toothache, broken tooth or swelling? Same-day emergency appointments — Call {PHONE}</a></div></div>')
    return (f'<div class="topbar"><div class="shell">'
            f'<a href="{GMB_URL}" target="_blank" rel="noopener" data-cta="topbar">{ic("pin")}{ADDRESS}</a>'
            f'<span>{ic("clock")}Open 7 am Mon–Thu · Saturday appointments</span>'
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
            f'<a class="brand" href="#top" aria-label="Belmont Dentistry Scottsdale — back to top"><img src="assets/img/logo-belmont-dentistry.webp" width="520" height="240" alt="Belmont Dentistry — Complete Dental Care"></a>'
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


DOCTORS = [
    ("Dr. Puneet Sandhu", "DDS", "Owner Dentist", "DDS · UCLA School of Dentistry", "assets/img/img-Dr-Puneet-Sandhu.webp",
     "A fun, easygoing family and cosmetic dentist who believes patients are partners in their own care. His passion is comprehensive and full-mouth reconstruction, backed by advanced implant and CEREC same-day crown training.",
     ["Spear Faculty Club", "Int’l Dental Implant Assoc.", "CEREC Mastery", "Implants & Full-Mouth Care"]),
    ("Dr. Ambreen Sandhu", "DDS", "Owner Dentist", "DDS with Honors · University of Detroit Mercy", "assets/img/img-Dr-Ambreen-Sandhu.webp",
     "Known for helping anxious patients feel at ease, “Dr. A” focuses on family, restorative and cosmetic dentistry and Invisalign — with an eye for aesthetic detail in every smile she designs.",
     ["Invisalign® Trained", "Spear Member", "Cosmetic & Family Care", "Anxious Patients Welcome"]),
    ("Dr. Erin Hong", "DDS", "Dentist", "DDS · UCLA School of Dentistry", "assets/img/img-Dr-Erin-Hong.webp",
     "Graduated from UCLA with awards in restorative and general dentistry, then completed a two-year hospital General Practice Residency in New York City as Chief Resident. A North Scottsdale local who is especially welcoming to patients returning after a long gap.",
     ["Hospital GPR · Chief Resident", "Family & General Dentistry", "Third-Generation Dentist"]),
]


def doctors_section(page, cls=""):
    cards = []
    for i, (name, suffix, role, cred, img, bio, tags) in enumerate(DOCTORS):
        t = "".join(f"<li>{x}</li>" for x in tags)
        first = name.split()[-1] if name != "Dr. Ambreen Sandhu" else "Dr. A"
        first = "Dr. " + first if not first.startswith("Dr.") else first
        cards.append(
            f'<article class="doc tilt" data-tilt="6" data-reveal style="--d:{i * .12:.2f}s">'
            f'<div class="doc-photo"><img src="{img}" width="467" height="611" loading="lazy" alt="{name}, {suffix} — dentist at Belmont Dentistry Scottsdale"><span class="doc-role">{role}</span></div>'
            f'<div class="doc-body"><h3>{name}, {suffix}</h3><div class="cred">{cred}</div><p>{bio}</p><ul class="doc-tags">{t}</ul>'
            f'{btn_book("Book with " + first, "btn btn-outline btn-block", "doctor")}</div></article>')
    title = ("Three Scottsdale Dentists. <em class=\"gold\">One Team That Knows You.</em>" if page == "np"
             else "Experienced Emergency Dentists <em class=\"gold\">You Can Trust</em>")
    lead = ("Three dentists, one office, and no handing you off to whoever is available — you see the dentist who already knows your chart."
            if page == "np" else
            "When you are in pain you want an experienced dentist, not a rotating associate. Our Scottsdale dentists handle extractions, root canals and same-day crowns right here in the office.")
    return (f'<section class="section {cls}" id="doctors"><div class="shell">{head_block("Meet Your Dentists", title, lead)}'
            f'<div class="carousel m-carousel cols-3" data-carousel><div class="carousel-track">{"".join(cards)}</div>'
            f'<div class="carousel-nav"><button class="carousel-btn" data-prev aria-label="Previous dentist">{ic("left")}</button><div class="dots"></div><button class="carousel-btn" data-next aria-label="Next dentist">{ic("right")}</button></div></div>'
            f'{section_cta(page, "doctors")}</div></section>')


def awards_section(page):
    badges = [
        ("star", f"{RATING}★ on Google", f"Average rating from {REVIEW_COUNT} Google reviews of our Scottsdale office"),
        ("award", "Spear Faculty Club", "Dr. Puneet Sandhu is a faculty member of Spear Education, the world’s largest dental education company"),
        ("heart", "Super Practice &amp; Patient’s Choice", "Recognized for an exceptional new-patient experience and an average rating above 4.8 stars"),
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
            f'<p>Advanced training, professional memberships and hundreds of happy Scottsdale patients.</p></div>'
            f'{carousel(b, "award", "m-carousel cols-3 badge-carousel", "badges")}'
            f'<div class="logo-strip" data-reveal><div class="logo-row">{l}</div></div>{section_cta(page, "awards")}</div></section>')


def insurance_section(page):
    ppo = ["We file your claims for you", "Benefits verified before treatment", "A clear estimate — no surprises at checkout", "FSA &amp; HSA funds welcome"]
    bdp = ["Exams, X-rays &amp; cleanings included", "Discounts on fillings, crowns, implants &amp; cosmetic care", "No annual maximums or waiting periods", "No claim forms — for individuals or the whole household"]
    cc = ["Convenient monthly payments", "Promotional financing plans*", "Use it for one crown or a full smile makeover", "Quick online application"]

    def lst(items):
        return "<ul>" + "".join(f"<li>{ic('check')}<span>{x}</span></li>" for x in items) + "</ul>"
    cards = (
        f'<div class="ins-card tilt" data-tilt="5" data-reveal><span class="icon-badge">{ic("shield")}</span><h3>In-Network with Most Major PPO Plans</h3>'
        f'<p>Our front office works with dental plans every day and helps you get the most from the benefits you already pay for.</p>{lst(ppo)}</div>'
        f'<div class="ins-card tilt" data-tilt="5" data-reveal style="--d:.1s"><span class="icon-badge">{ic("smile")}</span><h3>No Insurance? Join the Belmont Dental Plan</h3>'
        f'<p>A dental clinic for patients with no insurance shouldn’t mean paying full price. Our in-house membership costs less than traditional insurance.</p>{lst(bdp)}</div>'
        f'<div class="ins-card tilt" data-tilt="5" data-reveal style="--d:.2s"><span class="icon-badge">{ic("card")}</span><h3>Flexible Financing</h3>'
        f'<img class="cc-logo" src="assets/img/logo-carecredit.svg" alt="CareCredit" width="1106" height="150" loading="lazy">'
        f'<p>Start treatment now and pay over time with CareCredit, the healthcare credit card built for dental expenses.</p>{lst(cc)}</div>')
    pay = "".join(f"<span>{x}</span>" for x in ["Cash", "Checks", "Visa", "Mastercard", "American Express", "Discover", "CareCredit®", "FSA / HSA"])
    lead = ("Cost should never be the reason a small problem turns into a big one. We would rather spend ten minutes confirming your benefits than have you put off a visit because you’re unsure what it will cost."
            if page == "np" else
            "Pain shouldn’t have to wait on paperwork. Tell us your plan when you call and we’ll check your benefits — and if you don’t have insurance, you still have affordable options today.")
    return (f'<section class="insurance" id="insurance"><div class="bg"><img src="assets/img/img-dental-insurance-and-financing-banner-scottsdale.webp" alt="" loading="lazy" width="1920" height="1060"></div>'
            f'<div class="shell">{head_block("Insurance &amp; Financing", "Dental Insurance, Financing &amp; <em class=\"gold\">No-Insurance Options</em>", lead)}'
            f'{carousel(cards, "payment option", "m-carousel cols-3 ins-carousel", "ins-grid")}'
            f'<div class="pay-row" data-reveal><b>We accept</b>{pay}</div>'
            f'<div class="ins-callout" data-reveal>{ic("shield")}<p><strong>Not sure if we take your plan?</strong>Call {PHONE} — we’ll verify your benefits for free before your visit.</p>'
            f'<a class="btn btn-dark" {CALL} data-cta="insurance">{ic("phone", "ring-icon")}<span>Check My Insurance</span></a></div>'
            f'{section_cta(page, "insurance", "*CareCredit financing is subject to credit approval. Insurance coverage varies by plan.", dark=True)}</div></section>')


GALLERY = [
    ("img-belmont-dentistry-dental-clinic-building-exterior.webp", "Our Raintree Dr building"),
    ("img-belmont-dentistry-office-exterior-signage.webp", "Suite 115 entrance"),
    ("img-belmont-dentistry-dental-office-reception.webp", "Reception"),
    ("img-belmont-dentistry-waiting-room-interior.webp", "Waiting room"),
    ("img-belmont-dentistry-patient-lounge-interior.webp", "Patient lounge"),
    ("img-belmont-dentistry-modern-dental-treatment-room.webp", "Treatment room"),
    ("img-belmont-dentistry-window-view-treatment-room.webp", "Treatment rooms with a view"),
    ("img-belmont-dentistry-digital-dental-imaging-machine.webp", "3D CBCT imaging"),
    ("img-belmont-dentistry-digital-smile-design-tablet.webp", "Digital smile preview"),
    ("img-belmont-dentistry-modern-clinic-hallway.webp", "Inside our office"),
]


def gallery_section(page, cls=""):
    shots = "".join(f'<figure class="shot"><img src="assets/img/{f}" alt="Belmont Dentistry Scottsdale dental office — {c.lower()}" width="1200" height="860" loading="lazy"><figcaption>{c}</figcaption></figure>'
                    for f, c in GALLERY)
    lead = ("Tucked into Raintree Crossing near Northsight Blvd — a calm, modern office with TVs in every treatment room, warm blankets and noise-cancelling headphones."
            if page == "np" else
            "A calm, modern office in Raintree Crossing — with 3D imaging and in-office crown milling so most emergencies are handled right here.")
    return (f'<section class="section gallery {cls}" id="office"><div class="shell">{head_block("Office Tour", "Step Inside Our <em class=\"gold\">Scottsdale Dental Office</em>", lead)}'
            f'<div class="carousel" data-carousel data-auto data-reveal><div class="carousel-track">{shots}</div>'
            f'<div class="carousel-nav"><button class="carousel-btn" data-prev aria-label="Previous photo">{ic("left")}</button><div class="dots"></div><button class="carousel-btn" data-next aria-label="Next photo">{ic("right")}</button></div></div>'
            f'{section_cta(page, "gallery")}</div></section>')


def reviews_section(page, keys, cls=""):
    cards = "".join(review_card(k) for k in keys)
    title = "What Scottsdale Patients <em class=\"gold\">Say About Us</em>" if page == "np" else "Real Patients. <em class=\"gold\">Real Relief.</em>"
    score = (f'<a class="score-card" href="{GMB_URL}" target="_blank" rel="noopener" data-cta="reviews-score">'
             f'<span class="big">{RATING}</span><div>{stars()}<small>{GOOGLE_G}{REVIEW_COUNT} Google reviews</small></div></a>')
    return (f'<section class="section {cls}" id="reviews"><div class="shell">'
            f'<div class="reviews-top"><div class="section-head" data-reveal><span class="kicker">Real Google Reviews</span><h2>{title}</h2>'
            f'<p>Unedited Google reviews from patients of our Scottsdale office.</p></div><div data-reveal>{score}</div></div>'
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
    intro = ("Everything you need to know before your first visit to our Scottsdale dental office. Still have a question? Our front desk is happy to help."
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


def location_section(page):
    rows = "".join(f'<tr data-day="{d}"><td>{label}</td><td>{disp}</td></tr>' for _, label, disp, d in HOURS)
    directions = f'<a class="btn btn-ghost btn-block" href="{GMB_URL}" target="_blank" rel="noopener" data-cta="location-directions" style="margin-top:12px">{ic("nav")}<span>Get Directions</span></a>'
    if page == "ty":
        first = f'<a class="btn btn-gold btn-lg btn-block" href="{GMB_URL}" target="_blank" rel="noopener" data-cta="location-directions">{ic("nav")}<span>Get Directions</span></a>'
        second, directions = btn_call(f"Call {PHONE}", "btn btn-ghost btn-block", "location"), ""
    elif page == "em":
        first = btn_call(f"Call Now {PHONE}", "btn btn-red btn-lg btn-block btn-pulse", "location")
        second = btn_book("Book Online", "btn btn-ghost btn-block", "location")
    else:
        first = btn_book("Book Your Visit Online", "btn btn-gold btn-lg btn-block", "location")
        second = btn_call(f"Call {PHONE}", "btn btn-ghost btn-block", "location")
    title = {"np": "Your Local Dentist Near North Scottsdale &amp; <em class=\"gold\">Old Town</em>",
             "em": "Emergency Dentist Near You in <em class=\"gold\">Scottsdale</em>",
             "ty": "Getting to <em class=\"gold\">Our Scottsdale Office</em>"}[page]
    lead = {"np": "Easy to reach from North Scottsdale, Old Town, McCormick Ranch and Paradise Valley — in Raintree Crossing near Northsight Blvd, just off the Loop 101, with free parking.",
            "em": "Minutes from the Loop 101 at Raintree Dr &amp; Northsight Blvd — an easy drive from North Scottsdale, Old Town, Paradise Valley, Fountain Hills and North Phoenix.",
            "ty": "We’re in Raintree Crossing near Northsight Blvd, just off the Loop 101, with free parking right outside. Look for Suite 115."}[page]
    return (f'<section class="section" id="location"><div class="shell">{head_block("Location &amp; Contact", title, lead)}'
            f'<div class="location-grid" data-reveal="zoom">'
            f'<div class="map"><div class="map-fallback"><div><p><strong>Belmont Dentistry Scottsdale</strong><br>{ADDRESS}</p>'
            f'<a class="btn btn-outline" href="{GMB_URL}" target="_blank" rel="noopener" data-cta="map">{ic("nav")}<span>Get Directions</span></a></div></div>'
            f'<iframe src="{MAP_EMBED}" title="Map to Belmont Dentistry Scottsdale, {ADDRESS}" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe></div>'
            f'<div class="contact-card"><h3>Belmont Dentistry Scottsdale</h3>{rating_pill("location-rating")}'
            f'<div class="contact-row">{ic("pin")}<div><strong>Address</strong><a href="{GMB_URL}" target="_blank" rel="noopener" data-cta="location-address">{STREET}<br>{CITY_LINE}</a><br><small>Located in Raintree Crossing · Free parking</small></div></div>'
            f'<div class="contact-row">{ic("phone")}<div><strong>Call Us</strong><a {CALL} data-cta="location-phone">{PHONE}</a></div></div>'
            f'<div class="contact-row">{ic("clock")}<div style="flex:1"><strong>Office Hours</strong><span class="status" data-status style="margin-top:8px"><span class="live"></span><span class="label">Mon–Thu from 7 am</span></span></div></div>'
            f'<table class="hours" aria-label="Office hours">{rows}</table><p class="hours-note">*Friday &amp; Saturday hours run on alternate weeks — call to confirm.</p>'
            f'{first}{second}{directions}'
            f'</div></div></div></section>')


def final_cta(page):
    if page == "em":
        h = "Don’t Wait Out <em class=\"gold\">the Pain.</em>"
        p = "Dental problems rarely get better on their own. Call our Scottsdale emergency dentist now — we reserve time every day for patients in pain."
        btns = btn_call(f"Call Now {PHONE}", "btn btn-red btn-lg btn-pulse", "final") + btn_book("Book Online", "btn btn-ghost btn-lg", "final")
        chips = ["Same-day emergency visits", "New patients welcome", "Most PPO plans accepted"]
        img = "img-belmont-dentistry-modern-dental-treatment-room.webp"
    else:
        h = "Ready for a Dentist <em class=\"gold\">You’ll Actually Like?</em>"
        p = "New patients are welcome at our Scottsdale office. Book online in under a minute or call — our front desk will find a time that works, including early mornings and Saturdays."
        btns = btn_book("Book Your Visit Online", "btn btn-gold btn-lg", "final") + btn_call(f"Call {PHONE}", "btn btn-ghost btn-lg", "final")
        chips = ["Same-day appointments", "Most PPO plans accepted", "Belmont Dental Plan for no insurance"]
        img = "img-belmont-dentistry-waiting-room-seating.webp"
    c = "".join(f"<li>{ic('check')}{x}</li>" for x in chips)
    return (f'<section class="final-cta"><div class="bg"><img src="assets/img/{img}" alt="" loading="lazy" width="1200" height="860"></div>'
            f'<div class="shell" data-reveal="zoom"><span class="kicker">Belmont Dentistry Scottsdale</span><h2>{h}</h2><p>{p}</p>'
            f'<div class="btn-row">{btns}</div><ul class="chips">{c}</ul></div></section>')


def footer(page):
    legal = ("Same-day appointments depend on the schedule and the clinical situation. Insurance coverage varies by plan. "
             "CareCredit financing is subject to credit approval. Reviews are from Google; individual results vary.")
    return (f'<footer class="site-footer"><div class="shell"><img src="assets/img/logo-belmont-dentistry.webp" alt="Belmont Dentistry" width="520" height="240" loading="lazy">'
            f'<p><strong style="color:#fff">Belmont Dentistry Scottsdale</strong> · {ADDRESS} · <a {CALL} data-cta="footer">{PHONE}</a></p>'
            f'<p>© <span data-year>2026</span> Belmont Dentistry. All rights reserved.</p><p class="legal">{legal}</p></div></footer>')


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
             f'alt="Belmont Dentistry Scottsdale reception" width="510" height="683" loading="lazy"></div>')
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
        ("Monday", "07:00", "17:00"), ("Tuesday", "07:00", "18:00"), ("Wednesday", "07:00", "17:00"),
        ("Thursday", "07:00", "18:00"), ("Friday", "08:00", "15:00"), ("Saturday", "08:00", "14:00")]]
    reviews = [{"@type": "Review", "author": {"@type": "Person", "name": REVIEWS[k][0]},
                "reviewRating": {"@type": "Rating", "ratingValue": "5", "bestRating": "5"},
                "reviewBody": REVIEWS[k][2], "publisher": {"@type": "Organization", "name": "Google"}} for k in review_keys[:4]]
    dentist = {
        "@context": "https://schema.org", "@type": "Dentist", "@id": url + "#dentist",
        "name": "Belmont Dentistry Scottsdale", "description": desc, "url": url,
        "image": SITE + "/wp-content/uploads/2026/10/img-belmont-dentistry-office-exterior-signage.webp",
        "logo": SITE + "/wp-content/uploads/2026/10/cropped-img-Belmont-Dentistry-social-favicon.png",
        "telephone": "+1-480-602-8050", "priceRange": "$$", "hasMap": GMB_URL,
        "address": {"@type": "PostalAddress", "streetAddress": STREET, "addressLocality": "Scottsdale",
                    "addressRegion": "AZ", "postalCode": "85260", "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": 33.6219, "longitude": -111.8956},
        "areaServed": ["Scottsdale", "North Scottsdale", "Old Town Scottsdale", "Paradise Valley", "Phoenix"],
        "openingHoursSpecification": days,
        "aggregateRating": {"@type": "AggregateRating", "ratingValue": RATING, "reviewCount": REVIEW_COUNT, "bestRating": "5", "worstRating": "1"},
        "review": reviews,
        "employee": [{"@type": "Person", "name": f"{n}, {s}", "jobTitle": r} for n, s, r, *_ in DOCTORS],
        "paymentAccepted": "Cash, Check, Visa, Mastercard, American Express, Discover, CareCredit",
        "currenciesAccepted": "USD",
        "medicalSpecialty": "Dentistry",
        "availableService": [{"@type": "MedicalProcedure", "name": n} for n in (
            ["Emergency Dental Care", "Tooth Extraction", "Root Canal Therapy", "Same-Day CEREC Crowns", "Incision and Drainage"] if page == "em"
            else ["Dental Cleanings and Exams", "Dental Implants", "Invisalign", "Same-Day CEREC Crowns", "Teeth Whitening", "Emergency Dental Care"])],
    }
    faq = {"@context": "https://schema.org", "@type": "FAQPage",
           "mainEntity": [{"@type": "Question", "name": re.sub(r"<[^>]+>", "", q),
                           "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a)}} for q, a in faqs]}
    return ('<script type="application/ld+json">' + json.dumps(dentist, ensure_ascii=False) + "</script>\n"
            '<script type="application/ld+json">' + json.dumps(faq, ensure_ascii=False) + "</script>")


def document(page, title, desc, slug, body, faqs, review_keys, theme="#1E1B16", robots="noindex, follow", head_extra=""):
    url = LP_BASE + slug + "/"
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
{ld}
</head>
<body data-page="{slug}" id="top">
{GTM_BODY}
{sprite()}
{body}
<script src="assets/js/lp.js" defer></script>
</body>
</html>
"""


# ==========================================================================
# PAGE 1 — New patients / general dentist
# ==========================================================================
NP_FAQ = [
    ("Are you accepting new patients at your Scottsdale office?",
     f"Yes. Belmont Dentistry welcomes new patients of all ages at our Scottsdale office, including same-day and emergency appointments for anyone who needs prompt care. <a {BOOK}>Book online</a> or call {PHONE}."),
    ("Where is your Scottsdale dental office located?",
     f"We’re at {ADDRESS}, in the Raintree Crossing business corridor near Northsight Blvd — a short drive from North Scottsdale, Old Town Scottsdale and Paradise Valley, with free parking."),
    ("What are your office hours?",
     "Monday 7 am–5 pm, Tuesday 7 am–6 pm, Wednesday 7 am–5 pm, Thursday 7 am–6 pm, Friday 8 am–3 pm and Saturday 8 am–2 pm (Friday and Saturday on alternate weeks). We’re closed Sunday."),
    ("Which dental insurance plans do you accept?",
     f"We’re in-network with most major PPO dental insurance plans and file claims for you. Call {PHONE} and we’ll verify your benefits before your visit. Without insurance, you can join the Belmont Dental Plan or use CareCredit financing."),
    ("I don’t have dental insurance. Can I still be seen?",
     "Absolutely. Our in-house Belmont Dental Plan covers exams, X-rays and cleanings and gives you discounts on fillings, crowns, implants and cosmetic care — with no annual maximums, waiting periods or claim forms."),
    ("What happens at my first visit?",
     "You’ll get a tour of the office, a conversation about your dental history and concerns, a comprehensive exam with digital X-rays when needed and an oral cancer screening. Then we show you what we found on screen and give you a written plan — nothing is added that you didn’t agree to."),
    ("What should I bring to my first appointment?",
     "A photo ID, your dental insurance card if you have one, and a list of any current medications. Patient forms can be completed online ahead of time, and we can request your previous X-rays for you."),
    ("Do you see children and whole families?",
     "Yes. We see children from their first tooth through adults and seniors, and offer family appointments so parents and kids can be seen during the same visit — one Scottsdale family dentist for everyone."),
    ("What if I’m nervous about the dentist?",
     "You’re not alone and you won’t be judged. We offer noise-cancelling headphones, TVs in every room, warm blankets, nitrous oxide and oral conscious sedation, plus a calm, unhurried pace and a stop signal you control."),
    ("Can I get a permanent crown in one visit?",
     "Yes. With CEREC same-day technology we design, mill and place most ceramic crowns in about two hours — no temporary crown and no second appointment."),
    ("How much does a dental checkup cost?",
     "It depends on whether X-rays or additional screenings are needed and on your insurance coverage. We review your benefits and give you a cost estimate before your visit, and the Belmont Dental Plan is available if you don’t have insurance."),
]

NP_REVIEWS = ["liann", "art", "kaci", "wyn", "jennifer", "susan", "estela", "lisa"]


def page_new_patients():
    P = "np"
    hero = f"""
<section class="hero" id="hero">
  {hero_media("hero-poster-new-patients.webp", "hero-new-patients")}
  <div class="shell hero-grid">
    <div class="hero-copy">
      {rating_pill("hero-rating")}
      <p class="hero-eyebrow">Dentist in Scottsdale, AZ <span class="dot"></span> New Patients Welcome</p>
      <h1>Scottsdale’s Family Dentist, <em>Without the Wait.</em></h1>
      <p class="hero-lead">Same-day and next-day appointments, a <strong>permanent crown in a single visit</strong>, and a team that explains everything before it treats. Family-owned, in-network with most PPO plans and open from 7 am — plus Saturdays.</p>
      <div class="hero-ctas">
        {btn_book("Book Your Visit Online", "btn btn-gold btn-lg", "hero")}
        {btn_call(f"Call {PHONE}", "btn btn-ghost btn-lg btn-pulse", "hero")}
      </div>
      <p class="hero-micro">Booking takes under a minute · No insurance? Ask about the <a href="#insurance">Belmont Dental Plan</a></p>
      <ul class="chips">
        <li>{ic("zap")}Same-day appointments</li>
        <li>{ic("shield")}Most PPO plans accepted</li>
        <li>{ic("clock")}Open 7 am &amp; Saturdays</li>
        <li>{ic("heart")}Judgment-free care</li>
      </ul>
    </div>
    <aside class="hero-card" aria-label="New patient visit" data-reveal="right">
      <span class="card-badge">{ic("sparkles")}New Patients</span>
      <h2>Your First Visit, Made Easy</h2>
      <p class="sub">Here’s what every new patient gets at our Scottsdale dental office:</p>
      <ul class="ticks">
        <li><span class="tick">{ic("check")}</span>A tour of the office and a real conversation — never rushed</li>
        <li><span class="tick">{ic("check")}</span>Comprehensive exam, digital X-rays &amp; oral cancer screening</li>
        <li><span class="tick">{ic("check")}</span>Your X-rays on screen, plus a written plan with costs</li>
        <li><span class="tick">{ic("check")}</span>Insurance benefits checked for you before treatment</li>
      </ul>
      {btn_book("Book Online Now", "btn btn-gold btn-lg btn-block", "hero-card")}
      <p class="fine">Prefer to talk? <a {CALL} data-cta="hero-card">Call {PHONE}</a></p>
    </aside>
  </div>
  <span class="scroll-cue" aria-hidden="true"></span>
</section>"""

    st = stats([(f'{RATING}<span class="gold-text">★</span>', "Google rating"), (REVIEW_COUNT, "Google reviews"),
                ("3", "Scottsdale dentists"), ("7 am", "Early appointments")])

    offers = offers_section(P, [
        ("Fast Access", "Same-Day Visits", "Not weeks from now",
         "We hold time in the schedule every day for new patients and urgent needs, so many patients are seen the same or the next day.",
         "book", "Book Online", False),
        ("No Insurance?", "Belmont Dental Plan", "No maximums · No waiting periods",
         "Our in-house membership covers exams, X-rays and cleanings with discounts on fillings, crowns, implants and cosmetic care.",
         "call", "Call to Join", True),
        ("Insurance", "Free Benefits Check", "Before you sit down",
         "In-network with most major PPO plans. We file your claims and confirm what’s covered — including FSA/HSA dollars before they expire.",
         "call", "Check My Benefits", False),
        ("Financing", "Monthly Payments", "With CareCredit®",
         "Spread larger treatment into convenient monthly payments with promotional financing plans, subject to credit approval.",
         "book", "Book Online", False),
    ], [("headphones", "Noise-cancelling headphones"), ("monitor", "TVs in every room"), ("blanket", "Warm blankets"),
        ("coffee", "Complimentary beverages"), ("droplet", "Nitrous &amp; oral sedation"), ("parking", "Free parking")],
        "New Patient Offers", "Switching Dentists? <em class=\"gold\">We Make It Easy.</em>",
        "Whether it’s been six months or six years, there’s no judgment at our door — just a few perks that make starting with a new dentist in Scottsdale simple.")

    svc_cards = [
        ("img-Preventive-Care.webp", "Preventive Care", "Regular exams, cleanings and personalized preventive care to keep your smile healthy."),
        ("img-Dental-Implants.webp", "Dental Implants", "Restore missing teeth with durable, natural-looking implants — planned in 3D with CBCT imaging."),
        ("img-Invisalign.webp", "Invisalign®", "Straighten your smile discreetly with clear, comfortable aligners for teens and adults."),
        ("img-Emergency-Care.webp", "Emergency Care", "Prompt, compassionate care for dental pain, injuries and unexpected emergencies."),
    ]
    svc = "".join(f'<a class="svc tilt" data-tilt="7" {BOOK} data-cta="service" data-reveal style="--d:{i * .1:.1f}s">'
                  f'<img src="assets/img/{f}" alt="{t} at Belmont Dentistry Scottsdale" width="348" height="541" loading="lazy">'
                  f'<div class="svc-body"><h3>{t}</h3><p>{d}</p><span class="more">Book now {ic("arrow")}</span></div></a>'
                  for i, (f, t, d) in enumerate(svc_cards))
    svc_list = ["Cleanings &amp; Exams", "Digital X-Rays", "Oral Cancer Screenings", "Dental Sealants", "Composite Fillings", "Same-Day CEREC Crowns",
                "Root Canal Therapy", "Tooth Extractions", "Gum Disease Treatment", "Laser Dentistry", "Dental Bridges", "All-on-4 Implants",
                "Teeth Whitening", "Veneers &amp; Bonding", "Sedation Dentistry", "Smile Makeovers"]
    services = (f'<section class="section" id="services"><div class="shell">'
                f'{head_block("General &amp; Family Dentistry", "Complete Dental Care <em class=\"gold\">Under One Roof</em>", "Almost everything your family needs is handled right here in our Scottsdale dental clinic, by dentists who already know your history — from first cleanings to implants and Invisalign.")}'
                f'<div class="carousel m-carousel cols-4" data-carousel><div class="carousel-track">{svc}</div>'
                f'<div class="carousel-nav"><button class="carousel-btn" data-prev aria-label="Previous service">{ic("left")}</button><div class="dots"></div><button class="carousel-btn" data-next aria-label="Next service">{ic("right")}</button></div></div>'
                f'<ul class="svc-list" data-reveal>{"".join(f"<li>{ic("check")}{x}</li>" for x in svc_list)}</ul>'
                f'{section_cta(P, "services")}</div></section>')

    why = usp_section(P,
        [("zap", "A permanent crown in a single visit", "CEREC lets us complete most ceramic crowns in about two hours — no temporary, no second visit."),
         ("scan", "Implants planned in 3D first", "CBCT imaging shows bone volume, nerve position and sinus anatomy before any implant is placed."),
         ("clock", "Hours that fit a working week", "We open at 7 am four days a week, stay open until 6 pm and offer Saturday appointments.")],
        [("headphones", "Built for anxious patients", "Wireless headphones, TVs, iPads, blankets, beverages and a stop signal help you stay comfortable."),
         ("laser", "Gentler laser dentistry", "Our AMD laser treats gum and soft-tissue concerns with less bleeding, fewer stitches and faster healing."),
         ("shield", "Most PPO plans &amp; CareCredit", "We’re in-network with most major PPO plans, file your claims and offer CareCredit financing.")],
        "Why Scottsdale Patients <em class=\"gold\">Choose Belmont Dentistry</em>",
        "A privately owned practice — not a corporate chain — where your plan comes from your dentist and your appointment lasts as long as your mouth needs.",
        "img-Why-Scottsdale-Patients-Choose-Belmont-Dentistry.webp")

    them = ["Long waits for the next open slot, often weeks out", "Sitting in the waiting room past your appointment time", "A quick verbal summary before moving to the next patient",
            "A temporary crown for 2–3 weeks while a lab makes the real one", "Dental anxiety tolerated, not really addressed", "A different associate every visit", "Surprise costs discovered at checkout"]
    us = ["Early mornings and Saturday appointments, including same-day visits", "On-time appointments built around real treatment lengths", "Photos and X-rays reviewed on screen, with a written plan you keep",
          "A permanent CEREC crown designed, milled and placed in one visit", "Headphones, TVs, blankets and a calm chairside manner — every visit", "The same dentist and team who already know your history", "Benefits confirmed and costs reviewed before treatment begins"]
    us_col = f'<div class="compare-col us"><h3>Belmont Dentistry</h3><ul>{"".join(f"<li>{ic("check")}<span>{x}</span></li>" for x in us)}</ul></div>'
    them_col = f'<div class="compare-col them"><h3>A Typical Dental Office</h3><ul>{"".join(f"<li>{ic("x")}<span>{x}</span></li>" for x in them)}</ul></div>'
    compare = (f'<section class="section cream" id="difference"><div class="shell">'
               f'{head_block("The Belmont Difference", "Not Your Typical <em class=\"gold\">Dental Office</em>", "The difference shows up long before a drill ever comes out. Here’s why Scottsdale patients switch to us — and stay.")}'
               f'<div data-reveal="zoom">{carousel(us_col + them_col, "comparison", "m-carousel compare-carousel", "compare")}</div>'
               f'{section_cta(P, "compare")}</div></section>')

    steps = [("00:00", "Digital scan", "A 3D intraoral scanner captures the tooth in a few minutes. No trays, no impression putty."),
             ("00:20", "Crown design", "Software designs your crown to match your bite and the teeth beside it."),
             ("00:40", "In-office milling", "Our CEREC unit mills your crown from a solid ceramic block while you relax."),
             ("01:45", "Seat &amp; go", "We polish, check the bite and bond it in place. You leave with a permanent crown.")]
    tl = "".join(f'<div class="step" data-reveal style="--d:{i * .12:.2f}s"><span class="time">{t}</span><h4>{h}</h4><p>{p}</p></div>' for i, (t, h, p) in enumerate(steps))
    cerec = (f'<section class="section ink" id="same-day"><div class="shell"><div class="split">'
             f'<div class="split-copy left" data-reveal="left"><span class="kicker">Same-Day Technology</span>'
             f'<h2>Same-Day Crowns in Scottsdale: <em class="gold">One Visit, No Temporaries</em></h2>'
             f'<p>Most dental offices send your crown to an outside lab, fit a temporary and bring you back two or three weeks later. We mill your custom porcelain crown right here in the office, so the crown you leave with is the permanent one.</p>'
             f'<p>That means no impression putty, no temporary crown coming loose over a weekend, and no second round of time off work.</p>'
             f'<div class="btn-row" style="margin-top:26px">{btn_book("Book Your Crown Appointment", "btn btn-gold btn-lg", "cerec")}{btn_call(f"Call {PHONE}", "btn btn-ghost btn-lg", "cerec")}</div></div>'
             f'<div class="split-media tilt" data-tilt="6" data-reveal="right"><video data-lazy muted loop playsinline preload="none" poster="assets/img/cerec-poster.webp" aria-label="CEREC crown being milled in our Scottsdale office">'
             f'<source data-src="assets/video/cerec-milling.webm" type="video/webm"><source data-src="assets/video/cerec-milling.mp4" type="video/mp4"></video>'
             f'<span class="media-badge">{ic("zap")}Milled in-office in under 15 minutes</span></div></div>'
             f'<div class="timeline">{tl}</div></div></section>')

    visit = [("Book in under a minute", "Book online or call — same-day and next-day openings are often available for new patients."),
             ("Tour &amp; conversation", "Meet the team, see the office and talk through your dental history, goals and any worries."),
             ("Comprehensive exam", "A thorough exam with digital X-rays when needed and an oral cancer screening."),
             ("Your plan, in writing", "We show you what we found on screen, then give you a written plan with costs — what’s urgent, what can wait.")]
    vcards = "".join(f'<article class="step-card tilt" data-tilt="6" data-reveal style="--d:{i * .1:.1f}s"><h3>{h}</h3><p>{p}</p></article>' for i, (h, p) in enumerate(visit))
    bring = "".join(f"<li>{ic(i)}{t}</li>" for i, t in [("id", "Photo ID"), ("card", "Insurance card (if you have one)"), ("pill", "List of medications"), ("file", "Forms — online, before you arrive")])
    first_visit = (f'<section class="section cream" id="first-visit"><div class="shell">'
                   f'{head_block("Your First Visit", "What to Expect at <em class=\"gold\">Your First Visit</em>", "New patients are never rushed into treatment they don’t understand or want. Every recommendation comes with an explanation of why it matters and what happens if it waits.")}'
                   f'<div class="carousel m-carousel cols-4 steps" data-carousel><div class="carousel-track">{vcards}</div>'
                   f'<div class="carousel-nav"><button class="carousel-btn" data-prev aria-label="Previous step">{ic("left")}</button><div class="dots"></div><button class="carousel-btn" data-next aria-label="Next step">{ic("right")}</button></div></div>'
                   f'<ul class="perks" data-reveal><li style="background:var(--brown);color:#fff;border-color:var(--brown)">What to bring:</li>{bring}</ul>'
                   f'{section_cta(P, "first-visit")}</div></section>')

    body = "\n".join([
        topbar(P), site_header(P), "<main>", hero, st, offers, services,
        marquee(["Early Mornings &amp; Saturdays", "PPO Insurance Accepted", "Same-Day Technology", "Family Owned, Not Corporate", "New Patients Welcome", f"{RATING}★ on Google"]),
        why, compare, doctors_section(P), awards_section(P), cerec, insurance_section(P),
        reviews_section(P, NP_REVIEWS, "cream"), gallery_section(P), first_visit, faq_section(P, NP_FAQ), location_section(P), final_cta(P),
        "</main>", footer(P), sticky(P)])

    return document(
        P,
        "Scottsdale Dentist Near Me | New Patients Welcome | Belmont Dentistry",
        f"Looking for a dentist in Scottsdale, AZ? Belmont Dentistry is a family-owned Scottsdale dentist near North Scottsdale & Old Town with same-day appointments, most PPO plans and {RATING}★ from {REVIEW_COUNT} Google reviews. Book online.",
        "new-patients-scottsdale", body, NP_FAQ, NP_REVIEWS)


# ==========================================================================
# PAGE 2 — Emergency dentist
# ==========================================================================
EM_FAQ = [
    ("Can an emergency dentist see me the same day in Scottsdale?",
     f"Very often, yes. We reserve time every day for urgent needs, so many emergency patients are seen the same day they call. Availability depends on the schedule and your situation, so call {PHONE} as soon as symptoms start."),
    ("What counts as a dental emergency?",
     "Severe tooth pain, facial swelling, dental infections or abscesses, a knocked-out or broken tooth, a lost crown or filling, uncontrolled bleeding and damaged dentures can all need urgent care. If you’re unsure, call — we’ll help you decide the next step."),
    ("Do you do emergency tooth extractions in Scottsdale?",
     "Yes. Extractions are done on-site at our Scottsdale office, with bone grafting when needed to protect your options for an implant or bridge later. When a tooth can be saved, we’ll tell you how."),
    ("What should I do if my tooth gets knocked out?",
     "Handle the tooth by the crown (the chewing surface), avoid touching the root and keep it moist — in milk, or gently held back in the socket if you can. Call us right away; quick action improves the chance of saving the tooth."),
    ("Can a broken tooth be repaired during an emergency visit?",
     "In many cases, yes. Depending on the damage, treatment may include bonding, a filling or a same-day CEREC crown — designed, milled and placed in about two hours, with no temporary."),
    ("My crown or filling fell out. What should I do?",
     "Keep the crown if you have it, keep the area clean and avoid chewing on that side. Call us as soon as possible — an exposed tooth is more sensitive and at risk of further damage."),
    ("Do dental infections always need antibiotics?",
     "Not always. The right treatment depends on the source and severity of the infection — it may be drainage, a root canal or an extraction. We’ll evaluate it and recommend the right approach."),
    ("Do you treat children with dental emergencies?",
     "Yes. We provide emergency dental care for children, adults and seniors, with a calm approach that helps kids feel safe during an unexpected visit."),
    ("How much does an emergency dental visit cost?",
     "It depends on the exam, any X-rays needed and the treatment. We check your insurance benefits and explain costs before treatment, and patients without insurance can use the Belmont Dental Plan or CareCredit financing."),
    ("I’m in Phoenix — is your office close enough?",
     "Our Scottsdale office at Raintree Dr and Northsight Blvd is just off the Loop 101, an easy drive for patients coming from North Phoenix, Paradise Valley, Fountain Hills and across the Valley."),
]

EM_REVIEWS = ["lisa", "kaci", "wyn", "liann", "art", "susan", "jennifer", "estela"]


def page_emergency():
    P = "em"
    triage = [("flame", "Severe toothache"), ("broken", "Broken / cracked tooth"), ("droplet", "Swelling or abscess"), ("tooth", "Lost filling or crown"),
              ("alert", "Knocked-out tooth"), ("zap", "Tooth extraction"), ("smile", "Broken denture"), ("heart", "Gum pain / bleeding")]
    tri = "".join(f'<a {CALL} data-cta="triage">{ic(i)}<span>{t}</span></a>' for i, t in triage)
    hero = f"""
<section class="hero hero-emergency" id="hero">
  {hero_media("hero-poster-emergency.webp", "hero-emergency")}
  <div class="shell hero-grid">
    <div class="hero-copy">
      <div style="display:flex;flex-wrap:wrap;gap:10px;justify-content:inherit">{rating_pill("hero-rating")}<span class="status" data-status><span class="live"></span><span class="label">Same-day emergency appointments</span></span></div>
      <p class="hero-eyebrow">Same-Day Emergency Dental Care <span class="dot"></span> Scottsdale, AZ</p>
      <h1>Emergency Dentist in Scottsdale. <em>Get Seen Today.</em></h1>
      <p class="hero-lead">Severe toothache, a broken tooth, swelling or a lost crown? We <strong>reserve time every day for dental emergencies</strong>, so you can get out of pain fast — often the same day you call. New patients welcome, most PPO plans accepted.</p>
      <div class="hero-ctas">
        {btn_call(f"Call Now {PHONE}", "btn btn-red btn-lg btn-pulse", "hero")}
        {btn_book("Book Online", "btn btn-ghost btn-lg", "hero")}
      </div>
      <p class="hero-micro">Calling is the fastest way in — our team can often fit you in today.</p>
      <ul class="chips">
        <li>{ic("zap")}Same-day emergency visits</li>
        <li>{ic("tooth")}On-site extractions</li>
        <li>{ic("users")}New patients welcome</li>
        <li>{ic("clock")}Open from 7 am</li>
      </ul>
    </div>
    <aside class="hero-card" aria-label="Tell us what's wrong" data-reveal="right">
      <span class="card-badge red">{ic("siren")}Fast Pain Relief</span>
      <h2>What’s Going On?</h2>
      <p class="sub">Tap your problem to call our Scottsdale team directly.</p>
      <div class="triage">{tri}</div>
      {btn_call(f"Call {PHONE}", "btn btn-red btn-lg btn-block btn-pulse", "hero-card")}
      <p class="fine">or <a {BOOK} data-cta="hero-card">book online</a> — same-day slots when available</p>
    </aside>
  </div>
  <span class="scroll-cue" aria-hidden="true"></span>
</section>"""

    st = stats([("Same Day", "Emergency visits"), (f'{RATING}<span class="gold-text">★</span>', f"{REVIEW_COUNT} Google reviews"),
                ("7 am", "Opens Mon–Thu"), ("All Ages", "Kids, adults &amp; seniors")])

    conds = [
        ("flame", "Severe Toothache", "Throbbing pain that won’t ease up or keeps you awake — we find the cause and stop it.", ""),
        ("droplet", "Abscess &amp; Infection", "Swelling, pressure, a bad taste or a pimple on the gum. Infections need prompt care.", "Urgent"),
        ("broken", "Cracked or Broken Tooth", "From a small chip to a fractured tooth — often repaired with bonding or a same-day crown.", ""),
        ("tooth", "Lost Filling or Crown", "An exposed tooth is sensitive and at risk. Bring the crown with you if you have it.", ""),
        ("alert", "Knocked-Out Tooth", "Keep it moist and call immediately — quick action gives the best chance to save it.", "Minutes matter"),
        ("zap", "Emergency Tooth Extraction", "When a tooth can’t be saved, we remove it gently on-site — often the same day.", ""),
        ("smile", "Broken Dentures or Appliances", "Cracked dentures, partials or appliances repaired or replaced so you can eat and smile again.", ""),
        ("heart", "Gum Swelling &amp; Pain", "Sudden gum swelling, bleeding or tenderness evaluated and treated quickly.", ""),
    ]
    cc = "".join(f'<article class="cond tilt" data-tilt="6" data-reveal style="--d:{(i % 4) * .08:.2f}s">'
                 f'{f"<span class=urgent-tag>{u}</span>" if u else ""}<span class="icon-badge red">{ic(icn)}</span><h3>{t}</h3><p>{d}</p>'
                 f'<a class="call-link" {CALL} data-cta="condition">{ic("phone")}Call about this</a></article>'
                 for i, (icn, t, d, u) in enumerate(conds))
    conditions = (f'<section class="section" id="emergencies"><div class="shell">'
                  f'{head_block("Dental Emergencies We Treat", "Fast Relief for <em class=\"gold\">Every Dental Emergency</em>", "Not sure if it’s an emergency? If you’re in pain, bleeding, swollen or have damaged a tooth, call us — we’ll tell you exactly what to do next.")}'
                  f'<div class="carousel m-carousel cols-4" data-carousel><div class="carousel-track">{cc}</div>'
                  f'<div class="carousel-nav"><button class="carousel-btn" data-prev aria-label="Previous">{ic("left")}</button><div class="dots"></div><button class="carousel-btn" data-next aria-label="Next">{ic("right")}</button></div></div>'
                  f'{section_cta(P, "conditions")}</div></section>')

    aid = [
        ("alert", "Knocked-out tooth", "Hold it by the crown, never the root. Keep it moist in milk or gently back in the socket, and call us right away."),
        ("broken", "Broken or cracked tooth", "Save any pieces, rinse with warm water and hold a cold compress on your cheek to limit swelling."),
        ("droplet", "Swelling or abscess", "Use a cold compress — never heat — and call promptly. Swelling means an infection may be spreading."),
        ("tooth", "Lost filling or crown", "Keep the crown safe, keep the area clean and avoid chewing on that side until we see you."),
        ("flame", "Severe toothache", "Rinse with warm water and floss gently. Don’t put aspirin directly on the gums — it can burn the tissue."),
        ("snow", "Bleeding or soft-tissue injury", "Apply gentle pressure with clean gauze and a cold compress. Call us if bleeding doesn’t slow down."),
    ]
    ac = "".join(f'<article class="aid tilt" data-tilt="5" data-reveal style="--d:{(i % 3) * .1:.1f}s"><h3>{ic(icn)}{t}</h3><p>{d}</p></article>' for i, (icn, t, d) in enumerate(aid))
    first_aid = (f'<section class="section cream" id="first-aid"><div class="shell">'
                 f'{head_block("Before You Get Here", "What to Do <em class=\"gold\">Right Now</em>", "These steps from our Scottsdale team can protect your tooth and ease the pain while you’re on your way.")}'
                 f'<div class="carousel m-carousel cols-3" data-carousel><div class="carousel-track">{ac}</div>'
                 f'<div class="carousel-nav"><button class="carousel-btn" data-prev aria-label="Previous tip">{ic("left")}</button><div class="dots"></div><button class="carousel-btn" data-next aria-label="Next tip">{ic("right")}</button></div></div>'
                 f'<div class="er-warning" data-reveal>{ic("siren")}<p><strong>Go to the ER or call 911</strong> if you have trouble breathing or swallowing, swelling spreading to your eye or neck, uncontrolled bleeding, or a possible broken jaw. For everything else, call us first.</p></div>'
                 f'{section_cta(P, "first-aid")}</div></section>')

    tx = [("Same-day tooth extractions", "Done on-site, gently — with bone grafting when needed to keep future options open."),
          ("Emergency root canal therapy", "Removes the infection that causes throbbing pain, and saves the tooth."),
          ("Same-day CEREC crowns", "A broken tooth restored with a permanent crown in about two hours."),
          ("Incision &amp; drainage", "Fast relief from the pressure and swelling of a dental abscess."),
          ("Pulpotomies for kids", "Relieves nerve pain in children’s teeth while saving the tooth."),
          ("Bonding &amp; fillings", "Chips, cracks and lost fillings repaired to stop sensitivity fast.")]
    tlist = "".join(f'<li><span class="tick">{ic("check")}</span><div><strong>{t}</strong><span>{d}</span></div></li>' for t, d in tx)
    treatments = (f'<section class="section ink" id="services"><div class="shell"><div class="split">'
                  f'<div class="split-copy left" data-reveal="left"><span class="kicker">Emergency Treatment</span>'
                  f'<h2>We Don’t Just Numb It. <em class="gold">We Fix It.</em></h2>'
                  f'<p>Relief is the first step, not the whole job. Most emergency dental care is completed right here in our Scottsdale office, often in the same visit — from emergency tooth extraction to a same-day crown.</p>'
                  f'<ul class="checklist">{tlist}</ul>'
                  f'<div class="btn-row">{btn_call(f"Call Now {PHONE}", "btn btn-red btn-lg btn-pulse", "treatments")}{btn_book("Book Online", "btn btn-ghost btn-lg", "treatments")}</div></div>'
                  f'<div class="split-media tilt" data-tilt="6" data-reveal="right"><video data-lazy muted loop playsinline preload="none" poster="assets/img/cerec-poster.webp" aria-label="Same-day crown being milled in our Scottsdale office">'
                  f'<source data-src="assets/video/cerec-milling.webm" type="video/webm"><source data-src="assets/video/cerec-milling.mp4" type="video/mp4"></video>'
                  f'<span class="media-badge">{ic("zap")}Same-day crown, milled in-office</span></div></div></div></section>')

    proc = [("Tell us what happened", "We start with a conversation about your symptoms, when they started and what kind of pain you feel."),
            ("Exam of the problem area", "We check the tooth, gums and surrounding tissue for damage, swelling or infection."),
            ("Digital X-rays if needed", "Low-radiation X-rays reveal hidden infections and fractures we can’t see on the surface."),
            ("Clear options &amp; costs", "We explain what’s wrong, what can be done today and what it costs — before we start."),
            ("Relief-focused treatment", "Whenever possible, treatment begins in the same visit to stop the pain and protect the tooth."),
            ("A plan for what’s next", "If more care is needed, you leave with a clear plan, so you know exactly what comes next.")]
    pc = "".join(f'<article class="step-card tilt" data-tilt="6" data-reveal style="--d:{(i % 3) * .1:.1f}s"><h3>{h}</h3><p>{p}</p></article>' for i, (h, p) in enumerate(proc))
    process = (f'<section class="section" id="process"><div class="shell">'
               f'{head_block("Your Emergency Visit", "What Happens <em class=\"gold\">When You Arrive</em>", "An emergency appointment focuses on understanding the problem quickly and getting you relief — while protecting your long-term oral health.")}'
               f'<div class="carousel m-carousel cols-3 steps" data-carousel data-auto><div class="carousel-track">{pc}</div>'
               f'<div class="carousel-nav"><button class="carousel-btn" data-prev aria-label="Previous step">{ic("left")}</button><div class="dots"></div><button class="carousel-btn" data-next aria-label="Next step">{ic("right")}</button></div></div>'
               f'{section_cta(P, "process")}</div></section>')

    why = usp_section(P,
        [("zap", "Seen fast — often today", "We reserve time in the schedule every day for urgent needs, so you’re not waiting weeks in pain."),
         ("clock", "Early hours &amp; Saturdays", "Open from 7 am Monday to Thursday, until 6 pm Tuesdays and Thursdays, plus alternate Saturdays."),
         ("tooth", "Most treatment in-house", "Extractions, root canals and same-day CEREC crowns — handled here, not referred out.")],
        [("scan", "Answers you can see", "Digital X-rays and 3D CBCT imaging show exactly what’s wrong — on screen, explained in plain language."),
         ("headphones", "Calm, gentle care", "Nitrous oxide, oral conscious sedation, headphones and blankets for anxious or nervous patients."),
         ("shield", "Costs before treatment", "We check your insurance and explain costs up front. No surprise bills at checkout.")],
        "Why Scottsdale Calls Belmont <em class=\"gold\">First</em>",
        "A family-owned Scottsdale practice with the technology to fix most dental emergencies in one visit — and a team that genuinely cares.",
        "img-Why-Scottsdale-Patients-Choose-Belmont-Dentistry.webp")

    offers = offers_section(P, [
        ("Fast Access", "Same-Day Emergency Visits", "Time reserved every day",
         "Call as soon as symptoms start — many patients are seen the same day, and new patients are always welcome.",
         "call", "Call Now", True),
        ("Insurance", "Free Benefits Check", "Most major PPO plans",
         "We’re in-network with most PPO plans, file your claims and confirm coverage before treatment.",
         "call", "Check My Insurance", False),
        ("No Insurance?", "Belmont Dental Plan", "No maximums · No waiting periods",
         "Our in-house membership covers exams, X-rays and cleanings with discounts on treatment — no insurance needed.",
         "call", "Ask About the Plan", False),
        ("Financing", "Pay Over Time", "With CareCredit®",
         "Don’t let cost delay urgent care — split treatment into monthly payments, subject to credit approval.",
         "book", "Book Online", False),
    ], [("droplet", "Nitrous oxide"), ("pill", "Oral conscious sedation"), ("headphones", "Noise-cancelling headphones"),
        ("blanket", "Warm blankets"), ("child", "Kid-friendly care"), ("parking", "Free parking")],
        "Emergency Care Made Easy", "In Pain? No Insurance? <em class=\"gold\">We’ve Got You.</em>",
        "Getting out of pain shouldn’t be complicated. Here’s how we make emergency dental care in Scottsdale fast, comfortable and affordable.")

    body = "\n".join([
        topbar(P), site_header(P), "<main>", hero, st, conditions,
        marquee(["Same-Day Emergency Appointments", "On-Site Tooth Extractions", "Emergency Root Canals", "Same-Day CEREC Crowns", "Most PPO Plans Accepted", "Open 7 AM Mon–Thu"], red=True),
        first_aid, treatments, process, reviews_section(P, EM_REVIEWS, "cream"), why, offers, doctors_section(P),
        awards_section(P), insurance_section(P), gallery_section(P, "cream"), faq_section(P, EM_FAQ), location_section(P), final_cta(P),
        "</main>", footer(P), sticky(P)])

    return document(
        P,
        "Emergency Dentist Scottsdale, AZ | Same-Day Emergency Dental Care | Belmont Dentistry",
        f"In pain? Belmont Dentistry is an emergency dentist in Scottsdale, AZ with same-day emergency appointments, on-site tooth extractions, root canals and same-day crowns. {RATING}★ from {REVIEW_COUNT} Google reviews. Call {PHONE}.",
        "emergency-dentist-scottsdale", body, EM_FAQ, EM_REVIEWS, theme="#1E1B16")


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
  window.dataLayer.push({ event: 'thank_you_view', lp_page: 'thank-you-scottsdale', lp_source: src });
})();
</script>
"""


def page_thank_you():
    P = "ty"
    hero = f"""
<section class="hero ty-hero" id="hero">
  <div class="hero-media"><img src="assets/img/img-belmont-dentistry-waiting-room-interior.webp" alt="" width="1200" height="860" fetchpriority="high"></div>
  <img class="hero-watermark" src="assets/img/logo_watermark.svg" alt="" aria-hidden="true">
  <div class="shell">
    <div class="ty-check" aria-hidden="true"><svg viewBox="0 0 52 52"><circle cx="26" cy="26" r="24"/><path d="M15 27l7 7 15-16"/></svg></div>
    <p class="hero-eyebrow">Belmont Dentistry Scottsdale <span class="dot"></span> Request Received</p>
    <h1>Thank You! <em>We’ll See You Soon.</em></h1>
    <p class="hero-lead">Your request has been sent to our Scottsdale team. You’ll get a confirmation by text or email shortly — and if anything needs a quick check, we’ll call you from <strong>{PHONE}</strong>.</p>
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
         f'<a class="btn btn-dark btn-block" href="{SITE}/scottsdale-az/patient-forms/" target="_blank" rel="noopener" data-cta="forms">{ic("file")}<span>Patient Forms</span></a>'),
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
                  f'<div class="er-warning ty-help" data-reveal>{ic("siren")}<p><strong>Need to reschedule, or in pain before your appointment?</strong> Call {PHONE} — we reserve time every day for dental emergencies.</p>'
                  f'<a class="btn btn-red btn-pulse" {CALL} data-cta="ty-help">{ic("phone", "ring-icon")}<span>Call Now</span></a></div>'
                  f'</div></section>')

    team = "".join(f'<article class="team-mini" data-reveal style="--d:{i * .1:.1f}s"><img src="{img}" alt="{n}, {s}" width="467" height="611" loading="lazy">'
                   f'<h3>{n}, {s}</h3><span>{r} · {c.split(" · ")[-1]}</span></article>'
                   for i, (n, s, r, c, img, *_rest) in enumerate(DOCTORS))
    comfort = "".join(f"<li>{ic(i)}{t}</li>" for i, t in [("headphones", "Noise-cancelling headphones"), ("monitor", "TVs in every room"), ("blanket", "Warm blankets"),
                                                         ("coffee", "Complimentary beverages"), ("droplet", "Nitrous &amp; oral sedation"), ("heart", "A team that listens")])
    dentists = (f'<section class="section ink" id="dentists"><div class="shell">'
                f'{head_block("You’re in Good Hands", "Meet the Team <em class=\"gold\">Caring for You</em>", f"A family-owned Scottsdale practice rated {RATING}★ by {REVIEW_COUNT} Google reviewers. Here’s who you’ll meet.")}'
                f'<div class="team-grid">{team}</div>'
                f'<h3 class="ty-sub" data-reveal>Your comfort menu — included at every visit</h3><ul class="perks dark" data-reveal>{comfort}</ul>'
                f'<div class="section-cta" data-reveal><a class="btn btn-gold btn-lg" href="{GMB_URL}" target="_blank" rel="noopener" data-cta="dentists">{ic("star")}<span>Read Our {REVIEW_COUNT} Reviews</span></a>'
                f'{btn_call(f"Call {PHONE}", "btn btn-ghost btn-lg", "dentists")}</div></div></section>')

    body = "\n".join([site_header(P), "<main>", hero, next_steps, dentists, location_section(P), "</main>", footer(P), sticky(P)])
    return document(
        P,
        "Thank You | Belmont Dentistry Scottsdale",
        "Thank you for choosing Belmont Dentistry Scottsdale. Here’s what happens next, what to bring and how to find our office at 8350 E Raintree Dr, Suite 115.",
        "thank-you-scottsdale", body, None, None, robots="noindex, nofollow", head_extra=TY_DATALAYER)


# ==========================================================================
# Standalone (single-file) copies
# ==========================================================================
VIDEO_BASE_STANDALONE = "assets/video/"   # change to an absolute URL once the videos are uploaded


def bundle(src: Path, out: Path):
    text = src.read_text(encoding="utf-8")
    css = (HERE / "assets/css/belmont.css").read_text(encoding="utf-8")
    js = (HERE / "assets/js/lp.js").read_text(encoding="utf-8")

    def data_uri(rel):
        p = HERE / rel
        mime = mimetypes.guess_type(str(p))[0] or "application/octet-stream"
        if p.suffix == ".svg":
            mime = "image/svg+xml"
        elif p.suffix == ".webp":
            mime = "image/webp"
        return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode("ascii")

    text = text.replace('<link rel="stylesheet" href="assets/css/belmont.css">', f"<style>\n{css}\n</style>")
    text = text.replace('<script src="assets/js/lp.js" defer></script>', f"<script>\n{js}\n</script>")
    text = re.sub(r'(src|href|poster)="(assets/img/[^"]+)"', lambda m: f'{m.group(1)}="{data_uri(m.group(2))}"', text)
    text = text.replace('data-src="assets/video/', f'data-src="{VIDEO_BASE_STANDALONE}')
    out.write_text(text, encoding="utf-8")
    return out.stat().st_size


def main():
    pages = {
        "new-patients-scottsdale.html": page_new_patients(),
        "emergency-dentist-scottsdale.html": page_emergency(),
        "thank-you-scottsdale.html": page_thank_you(),
    }
    (HERE / "standalone").mkdir(exist_ok=True)
    for name, doc in pages.items():
        (HERE / name).write_text(doc, encoding="utf-8")
        size = bundle(HERE / name, HERE / "standalone" / name)
        print(f"wrote {name} ({len(doc) / 1024:.0f} KB) + standalone/{name} ({size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
