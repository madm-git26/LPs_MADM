#!/usr/bin/env python3
"""
Build the Belmont Dentistry Peoria Google Ads landing pages.

    new-patients-peoria.html        (new patient / general dentist)
    emergency-dentist-peoria.html   (emergency dentist)
    thank-you-peoria.html           (shared post-booking page)

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
# Practice facts — Peoria office only
# --------------------------------------------------------------------------
PHONE = "(623) 887-6008"          # Google Ads / CTM tracking number
TEL = "tel:+16238876008"
BOOK_URL = "https://book.allinone.dental/belmont-peoria?referrer_id=4"
GMB_URL = "https://maps.app.goo.gl/bR6qu6HvgyW5XJrz5"
MAP_EMBED = ("https://www.google.com/maps/embed?pb=!1m14!1m8!1m3!1d3322.818515901178!2d-112.23060311935829"
             "!3d33.610013030939776!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x872b69dc731df969%3A0xaaceda56012741bf"
             "!2sBelmont%20Dentistry%20Peoria!5e0!3m2!1sen!2sus!4v1790599951481!5m2!1sen!2sus")
STREET = "7966 W Thunderbird Rd, Suite 101"
CITY_LINE = "Peoria, AZ 85381"
ADDRESS = f"{STREET}, {CITY_LINE}"
RATING = "4.8"
REVIEW_COUNT = "426"          # Google, Peoria listing — read Oct 2026
SITE = "https://www.belmontdentistry.com"
LP_BASE = SITE + "/peoria-az/lp/"
CANONICAL = {  # the URLs the current Peoria landing pages live at
    "new-patients-peoria": LP_BASE + "my-new-patients/",
    "emergency-dentist-peoria": LP_BASE + "emergency-dentist/",
    "thank-you-peoria": LP_BASE + "thank-you/",
}

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

HOURS = [  # (schema day, label, display, js day index) — from belmontdentistry.com/peoria-az/
    ("Monday", "Monday*", "7:30 am – 5:00 pm", 1),
    ("Tuesday", "Tuesday", "7:30 am – 5:00 pm", 2),
    ("Wednesday", "Wednesday", "7:30 am – 5:00 pm", 3),
    ("Thursday", "Thursday", "7:30 am – 5:00 pm", 4),
    ("Friday", "Friday*", "7:30 am – 3:00 pm", 5),
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
# Real Google reviews of the Peoria office (verbatim, from the site's Peoria
# Google review feed, Oct 2026). Spelling kept as written by the patient.
# --------------------------------------------------------------------------
REVIEWS = {
    "joe": ("Joe Maus", "Emergency extraction",
            "I had a horrible toothache. They worked me into the schedule quickly. Unfortunately the tooth couldn't be saved and had to be pulled. It was a rather painless experience."),
    "sayla": ("Sayla Smile", "New patient",
              "I recently had my very 1st visit at Belmont Dentistry and I already feel like I’ve found my forever dentist. Dr. Powell was incredible, listened, was attentive and made me feel like a priority & not just a dollar sign. The entire staff was exceptional and made me feel welcomed. I appreciated the was pricing was very fair & well explained for my upcoming services. I give Belmont a 10/10!"),
    "christina": ("Christina Bonjorno", "Found her dentist",
                  "I tried several dentists before coming to Belmont dentistry. I have found my dentist in the valley. Highly recommend you coming in for your dental work. Dr. Powell is always through and walks you through step by step. Dr. Powell is the best!"),
    "patricia": ("Patricia Maryan", "Crown replacement",
                 "I am a longtime, very satisfied client of this practice and I was in need of a replacement for an ancient crown. Dr Powell and Maria, her able assistant, explained each step, accompanied by X-rays and other visuals, to put me at ease. It was the easiest and least painful dental procedure I have experienced. Dr Powell is an exacting practitioner of her craft, which made all the difference. Well done!"),
    "tammy": ("Tammy Schlieman", "Short wait",
              "Everyone was friendly and caring. They explained everything thoroughly and were very helpful. A huge plus was the very short wait time in the waiting room and treatment area."),
    "graden": ("Graden Clark", "Dr. Sandhu",
               "Dr. Sandhu and Maria were extremely knowledgeable and caring. They communicated well and listened carefully to my concerns. I feel that I am in good hands with them."),
    "shirley": ("Shirley Tracey", "Dr. Powell",
                "Dr Powell is a true professional, she is patient, understanding and accommodating when you have health issue. Her assistant is also very kind. The crown she replaced fits perfectly, no problems whatsoever with it . Very fortunate to have a dentist that works with you."),
    "lisa": ("Lisa Ruble", "Family dentist",
             "This will always be our family dentist. All the staff is wonderful!!"),
    "chris": ("Chris Collins", "Early appointment",
              "Went in fir a semiannual cleaning, appt. time 7:30, out the door by 8:10. Always friendky and thorough."),
    "cindy": ("Cindy Strozewski", "Whole team",
              "I’m so pleased with the care I receive at Belmont Dentistry in Peoria! Everyone in this practice is amazing! Vinni, my hygienist is great and Dr. Powell is amazing! This is a wonderful dental practice. 🦷. Thank you!"),
    "mary": ("Mary Otte", "Compassionate care", "Compassion and competence."),
}


def review_card(key):
    name, tag, text = REVIEWS[key]
    initials = "".join(w[0] for w in name.split()[:2]).upper()
    return (f'<figure class="review"><span class="quote-mark" aria-hidden="true">“</span>{stars()}'
            f'<span class="tagline">{tag}</span><blockquote>{text}</blockquote>'
            f'<footer><span class="avatar" aria-hidden="true">{initials}</span><div><strong>{name}</strong>'
            f'<small>{GOOGLE_G} Google review · Peoria</small></div></footer></figure>')


# --------------------------------------------------------------------------
# Shared sections
# --------------------------------------------------------------------------
def topbar(page):
    if page == "em":
        return (f'<div class="topbar urgent"><div class="shell"><a {CALL} data-cta="topbar">{ic("siren")}'
                f'Toothache, broken tooth or swelling? Emergency dental care in Peoria — Call {PHONE}</a></div></div>')
    return (f'<div class="topbar"><div class="shell">'
            f'<a href="{GMB_URL}" target="_blank" rel="noopener" data-cta="topbar">{ic("pin")}{ADDRESS}</a>'
            f'<span>{ic("clock")}Open from 7:30 am · Minutes from Arrowhead &amp; Glendale</span>'
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
            f'<a class="brand" href="#top" aria-label="Belmont Dentistry Peoria — back to top"><img src="assets/img/logo-belmont-dentistry.webp" width="520" height="240" alt="Belmont Dentistry — Complete Dental Care"></a>'
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
     "A fun, easygoing family and cosmetic dentist who believes patients are partners in their own care. He has years of experience in both emergency and restorative dentistry, backed by advanced implant and CEREC same-day crown training.",
     ["Spear Faculty Club", "Int’l Dental Implant Assoc.", "CEREC Mastery", "Emergency &amp; Restorative Care"], "Dr. Sandhu"),
    ("Dr. Jenneth Powell", "", "Dentist", "Midwestern University · Glendale, AZ", "assets/img/img-dr-jenneth.webp",
     "A collaborative, prevention-focused dentist who helps you understand the “why” behind every decision. Her favorite part of dentistry is helping patients overcome their fear — and her warm, empathetic approach has made her a trusted dentist for patients of all ages.",
     ["Prevention &amp; Education", "Anxious Patients Welcome", "Family Dentistry", "Patients of All Ages"], "Dr. Powell"),
]


def full_name(name, suffix):
    return f"{name}, {suffix}" if suffix else name


def doctors_section(page, cls=""):
    cards = []
    for i, (name, suffix, role, cred, img, bio, tags, first) in enumerate(DOCTORS):
        t = "".join(f"<li>{x}</li>" for x in tags)
        cards.append(
            f'<article class="doc tilt" data-tilt="6" data-reveal style="--d:{i * .12:.2f}s">'
            f'<div class="doc-photo"><img src="{img}" width="467" height="611" loading="lazy" alt="{full_name(name, suffix)} — dentist at Belmont Dentistry Peoria"><span class="doc-role">{role}</span></div>'
            f'<div class="doc-body"><h3>{full_name(name, suffix)}</h3><div class="cred">{cred}</div><p>{bio}</p><ul class="doc-tags">{t}</ul>'
            f'{btn_book("Book with " + first, "btn btn-outline btn-block", "doctor")}</div></article>')
    title = ("Meet Your Peoria Dentists. <em class=\"gold\">Care That Knows You.</em>" if page == "np"
             else "Experienced Emergency Dentists <em class=\"gold\">You Can Trust</em>")
    lead = ("Of all the Peoria dentists you could choose, you want one who knows your history. Our team provides attentive, consistent care — you see a dentist who understands your health, goals and comfort preferences."
            if page == "np" else
            "When you are in pain you want an experienced dentist, not a rotating associate. Our Peoria dentists handle emergency extractions, root canals and same-day crowns right here in the office.")
    return (f'<section class="section {cls}" id="doctors"><div class="shell">{head_block("Meet Your Dentists", title, lead)}'
            f'<div class="carousel m-carousel cols-2 doc-carousel" data-carousel><div class="carousel-track">{"".join(cards)}</div>'
            f'<div class="carousel-nav"><button class="carousel-btn" data-prev aria-label="Previous dentist">{ic("left")}</button><div class="dots"></div><button class="carousel-btn" data-next aria-label="Next dentist">{ic("right")}</button></div></div>'
            f'{section_cta(page, "doctors")}</div></section>')


def awards_section(page):
    badges = [
        ("star", f"{RATING}★ on Google", f"Average rating from {REVIEW_COUNT} Google reviews of our Peoria office"),
        ("award", "Spear Faculty Club", "Dr. Puneet Sandhu is a faculty member of Spear Education, the world’s largest dental education company"),
        ("heart", "Patient’s Choice 2023 &amp; Super Practice", "Recognized for an exceptional new-patient experience and top patient ratings in Peoria"),
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
            f'<p>Advanced training, professional memberships and hundreds of happy Peoria patients.</p></div>'
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
    return (f'<section class="insurance" id="insurance"><div class="bg"><img src="assets/img/img-dental-insurance-and-financing-banner-peoria.webp" alt="" loading="lazy" width="1600" height="883"></div>'
            f'<div class="shell">{head_block("Insurance &amp; Financing", "Dental Insurance, Financing &amp; <em class=\"gold\">No-Insurance Options</em>", lead)}'
            f'{carousel(cards, "payment option", "m-carousel cols-3 ins-carousel", "ins-grid")}'
            f'<div class="pay-row" data-reveal><b>We accept</b>{pay}</div>'
            f'<div class="ins-callout" data-reveal>{ic("shield")}<p><strong>Not sure if we take your plan?</strong>Call {PHONE} — we’ll verify your benefits for free before your visit.</p>'
            f'<a class="btn btn-dark" {CALL} data-cta="insurance">{ic("phone", "ring-icon")}<span>Check My Insurance</span></a></div>'
            f'{section_cta(page, "insurance", "*CareCredit financing is subject to credit approval. Insurance coverage varies by plan.", dark=True)}</div></section>')


GALLERY = [  # the Peoria office's own photos (belmontdentistry.com/peoria-az/office-tour/)
    ("img-belmont-dentistry-clinic-exterior-building.webp", "Our W Thunderbird Rd office"),
    ("img-belmont-dentistry-front-desk-reception-area.webp", "Reception"),
    ("img-belmont-dentistry-patient-waiting-room.webp", "Waiting room"),
    ("img-belmont-dentistry-modern-dental-operatory.webp", "Treatment room"),
    ("img-belmont-dentistry-dental-chair-with-window.webp", "Treatment rooms with a view"),
    ("img-belmont-dentistry-dental-office-interior.webp", "Inside our office"),
    ("img-belmont-dentistry-clinic-hallway-interior.webp", "Our hallway"),
    ("img-belmont-dentistry-dental-cerec-machine.webp", "In-office CEREC milling"),
    ("img-belmont-dentistry-digital-dental-imaging-machines.webp", "3D CBCT imaging"),
    ("img-belmont-dentistry-panoramic-dental-x-ray-machine.webp", "Digital X-rays"),
]


def gallery_section(page, cls=""):
    shots = "".join(f'<figure class="shot"><img src="assets/img/{f}" alt="Belmont Dentistry Peoria dental office — {c.lower()}" width="960" height="640" loading="lazy"><figcaption>{c}</figcaption></figure>'
                    for f, c in GALLERY)
    lead = ("A calm, modern local dentist office on W Thunderbird Rd — with TVs in every treatment room, warm blankets and noise-cancelling headphones."
            if page == "np" else
            "A calm, modern emergency dental clinic on W Thunderbird Rd — with 3D imaging and in-office crown milling so most emergencies are handled right here.")
    return (f'<section class="section gallery {cls}" id="office"><div class="shell">{head_block("Office Tour", "Step Inside Our <em class=\"gold\">Peoria Dental Office</em>", lead)}'
            f'<div class="carousel" data-carousel data-auto data-reveal><div class="carousel-track">{shots}</div>'
            f'<div class="carousel-nav"><button class="carousel-btn" data-prev aria-label="Previous photo">{ic("left")}</button><div class="dots"></div><button class="carousel-btn" data-next aria-label="Next photo">{ic("right")}</button></div></div>'
            f'{section_cta(page, "gallery")}</div></section>')


def reviews_section(page, keys, cls=""):
    cards = "".join(review_card(k) for k in keys)
    title = "What Peoria Patients <em class=\"gold\">Say About Us</em>" if page == "np" else "Real Patients. <em class=\"gold\">Real Relief.</em>"
    score = (f'<a class="score-card" href="{GMB_URL}" target="_blank" rel="noopener" data-cta="reviews-score">'
             f'<span class="big">{RATING}</span><div>{stars()}<small>{GOOGLE_G}{REVIEW_COUNT} Google reviews</small></div></a>')
    return (f'<section class="section {cls}" id="reviews"><div class="shell">'
            f'<div class="reviews-top"><div class="section-head" data-reveal><span class="kicker">Real Google Reviews</span><h2>{title}</h2>'
            f'<p>Unedited Google reviews from patients of our Peoria office.</p></div><div data-reveal>{score}</div></div>'
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
    intro = ("Everything you need to know before your first visit to our Peoria dental office. Still have a question? Our front desk is happy to help."
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
    title = {"np": "Your Local Dentist Office Near <em class=\"gold\">Arrowhead &amp; Glendale</em>",
             "em": "Peoria Emergency Dentist <em class=\"gold\">Near You</em>",
             "ty": "Getting to <em class=\"gold\">Our Peoria Office</em>"}[page]
    lead = {"np": "Looking for a dentist near your location? We’re on W Thunderbird Rd in Peoria — minutes from Arrowhead, Glendale, Sun City and Surprise, with free parking at the office.",
            "em": "Your emergency dental clinic on W Thunderbird Rd — an easy drive from Arrowhead, Glendale, Sun City, Surprise and the rest of the West Valley.",
            "ty": "We’re on W Thunderbird Rd with free parking right outside. Look for Suite 101."}[page]
    return (f'<section class="section" id="location"><div class="shell">{head_block("Location &amp; Contact", title, lead)}'
            f'<div class="location-grid" data-reveal="zoom">'
            f'<div class="map"><div class="map-fallback"><div><p><strong>Belmont Dentistry Peoria</strong><br>{ADDRESS}</p></div></div>'
            f'<iframe src="{MAP_EMBED}" title="Map to Belmont Dentistry Peoria, {ADDRESS}" loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe>{directions}</div>'
            f'<div class="contact-card"><div class="cc-head"><h3>Belmont Dentistry Peoria</h3>{rating_pill("location-rating")}</div>'
            f'<div class="cc-info">'
            f'<a class="cc-item" href="{GMB_URL}" target="_blank" rel="noopener" data-cta="location-address">{ic("pin")}<span><strong>Address</strong>{STREET}, {CITY_LINE}<small>Free parking at the office</small></span></a>'
            f'<a class="cc-item" {CALL} data-cta="location-phone">{ic("phone")}<span><strong>Call Us</strong>{PHONE}<small>Tap to call</small></span></a></div>'
            f'<div class="cc-hours"><div class="cc-hours-head"><strong>{ic("clock")}Office Hours</strong>'
            f'<span class="status" data-status><span class="live"></span><span class="label">Tue–Thu from 7:30 am</span></span></div>'
            f'<div class="hours" role="table" aria-label="Office hours">{rows}</div><p class="hours-note">*Monday &amp; Friday hours run on alternate weeks — call to confirm.</p></div>'
            f'<div class="cc-btns">{first}{second}</div>'
            f'</div></div></div></section>')


def final_cta(page):
    if page == "em":
        h = "Don’t Wait Out <em class=\"gold\">the Pain.</em>"
        p = "Dental problems rarely get better on their own. Call our Peoria emergency dentist now — we make every effort to see you the same day."
        btns = btn_call(f"Call Now {PHONE}", "btn btn-red btn-lg btn-pulse", "final") + btn_book("Book Online", "btn btn-ghost btn-lg", "final")
        chips = ["Same-day emergency visits", "Emergency extractions", "Most PPO plans accepted"]
        img = "img-belmont-dentistry-modern-dental-operatory.webp"
    else:
        h = "Ready for a Dentist <em class=\"gold\">You’ll Actually Like?</em>"
        p = "New patients are welcome at our Peoria office. Book online in under a minute or call — most new patients are seen within a few days, with appointments from 7:30 am."
        btns = btn_book("Book Your Visit Online", "btn btn-gold btn-lg", "final") + btn_call(f"Call {PHONE}", "btn btn-ghost btn-lg", "final")
        chips = ["Appointments within days", "Most PPO plans accepted", "Belmont Dental Plan for no insurance"]
        img = "img-belmont-dentistry-patient-waiting-room.webp"
    c = "".join(f"<li>{ic('check')}{x}</li>" for x in chips)
    return (f'<section class="final-cta"><div class="bg"><img src="assets/img/{img}" alt="" loading="lazy" width="960" height="640"></div>'
            f'<div class="shell" data-reveal="zoom"><span class="kicker">Belmont Dentistry Peoria</span><h2>{h}</h2><p>{p}</p>'
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
             f'alt="Belmont Dentistry Peoria reception" width="510" height="683" loading="lazy"></div>')
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
        ("Monday", "07:30", "17:00"), ("Tuesday", "07:30", "17:00"), ("Wednesday", "07:30", "17:00"),
        ("Thursday", "07:30", "17:00"), ("Friday", "07:30", "15:00")]]
    reviews = [{"@type": "Review", "author": {"@type": "Person", "name": REVIEWS[k][0]},
                "reviewRating": {"@type": "Rating", "ratingValue": "5", "bestRating": "5"},
                "reviewBody": REVIEWS[k][2], "publisher": {"@type": "Organization", "name": "Google"}} for k in review_keys[:4]]
    dentist = {
        "@context": "https://schema.org", "@type": "Dentist", "@id": url + "#dentist",
        "name": "Belmont Dentistry Peoria", "description": desc, "url": url,
        "image": SITE + "/wp-content/uploads/2026/10/img-belmont-dentistry-clinic-exterior-building.webp",
        "logo": SITE + "/wp-content/uploads/2026/10/cropped-img-Belmont-Dentistry-social-favicon.png",
        "telephone": "+1-623-887-6008", "priceRange": "$$", "hasMap": GMB_URL,
        "address": {"@type": "PostalAddress", "streetAddress": STREET, "addressLocality": "Peoria",
                    "addressRegion": "AZ", "postalCode": "85381", "addressCountry": "US"},
        "geo": {"@type": "GeoCoordinates", "latitude": 33.6100, "longitude": -112.2306},
        "areaServed": ["Peoria", "Glendale", "Arrowhead", "Sun City", "Surprise"],
        "openingHoursSpecification": days,
        "aggregateRating": {"@type": "AggregateRating", "ratingValue": RATING, "reviewCount": REVIEW_COUNT, "bestRating": "5", "worstRating": "1"},
        "review": reviews,
        "employee": [{"@type": "Person", "name": full_name(n, s), "jobTitle": r} for n, s, r, *_ in DOCTORS],
        "paymentAccepted": "Cash, Check, Visa, Mastercard, American Express, Discover, CareCredit",
        "currenciesAccepted": "USD",
        "medicalSpecialty": "Dentistry",
        "availableService": [{"@type": "MedicalProcedure", "name": n} for n in (
            ["Emergency Dental Care", "Emergency Tooth Extraction", "Root Canal Therapy", "Same-Day CEREC Crowns", "Incision and Drainage"] if page == "em"
            else ["Dental Cleanings and Exams", "Dental Implants", "Invisalign", "Same-Day CEREC Crowns", "Teeth Whitening", "Emergency Dental Care"])],
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
    ("Are you accepting new patients at your Peoria dental office?",
     f"Yes. We welcome new patients of all ages. Most people can be scheduled within a few days, and your first visit includes a full exam, digital X-rays and a clear written plan. <a {BOOK}>Book online</a> in under a minute or call {PHONE}."),
    ("Where is your Peoria office located?",
     f"We’re at {ADDRESS} — easy to reach from Arrowhead, Glendale, Sun City and Surprise, with free parking at the office."),
    ("What are your office hours? Is there a dentist open today?",
     f"Looking for dentists that are open near you today? We’re open Tuesday to Thursday 7:30 am–5 pm, plus Monday 7:30 am–5 pm and Friday 7:30 am–3 pm on alternate weeks. We’re closed Saturday and Sunday. The live status in the location section shows whether we’re open right now — or call {PHONE} for the earliest opening."),
    ("Which dental insurance plans do you accept?",
     f"We’re in-network with most major PPO dental plans, and we file your claims for you. Call {PHONE} and our front office will check your benefits before your visit so there are no surprises. We can also help you use FSA or HSA funds before they expire at year-end."),
    ("I don’t have dental insurance. Can I still be seen?",
     "Absolutely. Our in-house Belmont Dental Plan covers exams, X-rays and cleanings and gives you savings on fillings, crowns, implants and cosmetic care — with no annual maximums, waiting periods or claim forms. CareCredit financing can also spread larger treatment into monthly payments, subject to credit approval."),
    ("What should I expect at my first visit?",
     "Your first visit starts with a conversation about your goals and concerns. We take digital X-rays and intraoral photos, complete a thorough exam and show you the images on screen. You leave with a written plan that separates urgent needs from optional treatment, with costs and expected insurance coverage for each stage."),
    ("Are you a family dentist? Do you see children?",
     "Yes. Belmont Dentistry is a family dental practice, so parents and children can be seen at the same office and often at the same visit. We keep appointments calm and friendly so kids build a positive relationship with dental care from the start."),
    ("What if I’m nervous about going to the dentist?",
     "Many of our patients feel the same way. Wireless headphones, TVs, warm blankets and a simple stop signal put you in control. We explain every step before it happens, and we never rush you or judge how long it has been since your last visit."),
    ("Do you offer Invisalign or orthodontic treatment in Peoria?",
     "Yes. We offer Invisalign clear aligners for teens and adults who want straighter teeth without metal braces. A consultation includes a digital scan, a preview of the expected result, a timeline and a clear cost, so you know exactly what to expect before you commit."),
    ("Can I get a same-day crown in Peoria?",
     "In most cases, yes. Our CEREC system scans the tooth, designs the crown and mills it from solid ceramic right in our office. You leave the same day with a permanent, shade-matched crown and no temporary to worry about."),
    ("Is your office convenient if I live in Glendale?",
     "Yes. Our office on W Thunderbird Rd is a short drive for patients in Glendale, Arrowhead, Sun City, Surprise and across the West Valley — with free parking right outside."),
]

NP_REVIEWS = ["sayla", "christina", "patricia", "lisa", "tammy", "chris", "graden", "cindy"]


def page_new_patients():
    P = "np"
    hero = f"""
<section class="hero" id="hero">
  {hero_media("hero-poster-new-patients.webp", "hero-new-patients")}
  <div class="shell hero-grid">
    <div class="hero-copy">
      {rating_pill("hero-rating")}
      <p class="hero-eyebrow">Dentist in Peoria, AZ <span class="dot"></span> New Patients Welcome</p>
      <h1>Peoria’s Family Dentist. <em>Never Rushed, Never Judged.</em></h1>
      <p class="hero-lead">Searching for the best dentist in Peoria, AZ? Our family-owned office on W Thunderbird Rd sees most new patients <strong>within a few days</strong>, makes a <strong>permanent crown in a single visit</strong>, and explains everything before it treats — minutes from Arrowhead and Glendale.</p>
      <div class="hero-ctas">
        {btn_book("Book Your Visit Online", "btn btn-gold btn-lg", "hero")}
        {btn_call(f"Call {PHONE}", "btn btn-ghost btn-lg btn-pulse", "hero")}
      </div>
      <p class="hero-micro">Booking takes under a minute · No insurance? Ask about the <a href="#insurance">Belmont Dental Plan</a></p>
      <ul class="chips">
        <li>{ic("zap")}Appointments within days</li>
        <li>{ic("shield")}Most PPO plans accepted</li>
        <li>{ic("clock")}Open from 7:30 am</li>
        <li>{ic("heart")}Judgment-free care</li>
      </ul>
    </div>
    <aside class="hero-card" aria-label="New patient visit" data-reveal="right">
      <span class="card-badge">{ic("sparkles")}New Patients</span>
      <h2>Your First Visit, Made Easy</h2>
      <p class="sub">Here’s what every new patient gets at our Peoria dental office:</p>
      <ul class="ticks">
        <li><span class="tick">{ic("check")}</span>A tour of the office and a real conversation — never rushed</li>
        <li><span class="tick">{ic("check")}</span>Comprehensive exam with low-radiation digital X-rays</li>
        <li><span class="tick">{ic("check")}</span>Professional cleaning and a personal consultation</li>
        <li><span class="tick">{ic("check")}</span>Insurance benefits reviewed to maximize your coverage</li>
      </ul>
      {btn_book("Book Online Now", "btn btn-gold btn-lg btn-block", "hero-card")}
      <p class="fine">Prefer to talk? <a {CALL} data-cta="hero-card">Call {PHONE}</a></p>
    </aside>
  </div>
  <span class="scroll-cue" aria-hidden="true"></span>
</section>"""

    st = stats([(f'{RATING}<span class="gold-text">★</span>', "Google rating"), (REVIEW_COUNT, "Google reviews"),
                ("2", "Peoria dentists"), ("7:30 am", "Early appointments")])

    offers = offers_section(P, [
        ("Fast Access", "Seen Within Days", "Not weeks from now",
         "Most new patients can be scheduled within a few days — and dental emergencies are often seen the same day you call.",
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
        "Searching for family dentists near me? Whether it’s been six months or six years, there’s no judgment at our door — just a few perks that make switching to a new family dentist in Peoria simple.")

    svc_cards = [
        ("img-preventive-care.webp", "Preventive Care", "Cleanings, exams, digital X-rays and oral cancer screenings that catch small problems early."),
        ("img-dental-implants-1.webp", "Dental Implants", "Replace missing teeth with strong, natural-looking implants planned with 3D imaging."),
        ("img-invisialign.webp", "Invisalign®", "Straighten teeth with clear aligners that fit around work, school and everyday life."),
        ("img-emergency-care.webp", "Emergency Care", "Fast, caring treatment for toothaches, broken teeth and dental injuries — often the same day."),
    ]
    svc = "".join(f'<a class="svc tilt" data-tilt="7" {BOOK} data-cta="service" data-reveal style="--d:{i * .1:.1f}s">'
                  f'<img src="assets/img/{f}" alt="{t} at Belmont Dentistry Peoria" width="348" height="541" loading="lazy">'
                  f'<div class="svc-body"><h3>{t}</h3><p>{d}</p><span class="more">Book now {ic("arrow")}</span></div></a>'
                  for i, (f, t, d) in enumerate(svc_cards))
    svc_list = ["Cleanings &amp; Exams", "Digital X-Rays", "Oral Cancer Screenings", "Dental Sealants", "Composite Fillings", "Same-Day CEREC Crowns",
                "Root Canal Therapy", "Tooth Extractions", "Gum Disease Treatment", "Laser Dentistry", "Dental Bridges", "All-on-4 Implants",
                "Teeth Whitening", "Veneers &amp; Bonding", "Sedation Dentistry", "Smile Makeovers"]
    services = (f'<section class="section" id="services"><div class="shell">'
                f'{head_block("General &amp; Family Dentistry", "Complete Dental Care <em class=\"gold\">Under One Roof</em>", "Looking for a local dentist in your area who can handle it all? General, cosmetic, restorative and emergency dentistry are all under one roof in our Peoria office — by a team that already knows your history.")}'
                f'<div class="carousel m-carousel cols-4" data-carousel><div class="carousel-track">{svc}</div>'
                f'<div class="carousel-nav"><button class="carousel-btn" data-prev aria-label="Previous service">{ic("left")}</button><div class="dots"></div><button class="carousel-btn" data-next aria-label="Next service">{ic("right")}</button></div></div>'
                f'<ul class="svc-list" data-reveal>{"".join(f"<li>{ic("check")}{x}</li>" for x in svc_list)}</ul>'
                f'{section_cta(P, "services")}</div></section>')

    why = usp_section(P,
        [("zap", "Same-day crowns, no temporary", "With CEREC, many ceramic crowns are designed, made and placed in one visit — no return trip."),
         ("scan", "Implants planned in 3D", "CBCT imaging shows bone levels, nerves and sinus anatomy before implant treatment is planned."),
         ("clock", "Appointments around your week", "Early-morning appointments from 7:30 am make it easier to fit dental care around work.")],
        [("headphones", "Comfort for nervous patients", "Wireless headphones, TVs, warm blankets and a simple stop signal whenever you need a break."),
         ("laser", "Precise laser gum care", "Laser dentistry treats certain gum and soft-tissue concerns with less bleeding and fewer stitches."),
         ("shield", "Clear insurance &amp; payment", "In-network with most major PPO plans, plus CareCredit financing for qualified patients.")],
        "What Sets Our Peoria <em class=\"gold\">Dental Office Apart</em>",
        "A privately owned practice — not a corporate chain — so treatment recommendations come from the dentist who examines you, and appointments are as long as your mouth needs.",
        "img-belmont-dentistry-front-desk-reception-area.webp")

    them = ["Long waits for the next open slot, often weeks out", "Sitting in the waiting room past your appointment time", "A quick verbal summary before moving to the next patient",
            "A temporary crown for 2–3 weeks while a lab makes the real one", "Dental anxiety tolerated, not really addressed", "A different associate every visit", "Surprise costs discovered at checkout"]
    us = ["Early-morning appointments from 7:30 am — usually within a few days", "On-time appointments built around real treatment lengths", "Photos and X-rays reviewed on screen, with a written plan you keep",
          "A permanent CEREC crown designed, milled and placed in one visit", "Headphones, TVs, blankets and a calm chairside manner — every visit", "The same dentist and team who already know your history", "Benefits confirmed and costs reviewed before treatment begins"]
    us_col = f'<div class="compare-col us"><h3>Belmont Dentistry</h3><ul>{"".join(f"<li>{ic("check")}<span>{x}</span></li>" for x in us)}</ul></div>'
    them_col = f'<div class="compare-col them"><h3>A Typical Dental Office</h3><ul>{"".join(f"<li>{ic("x")}<span>{x}</span></li>" for x in them)}</ul></div>'
    compare = (f'<section class="section cream" id="difference"><div class="shell">'
               f'{head_block("The Belmont Difference", "Not Your Typical <em class=\"gold\">Dental Office</em>", "The difference shows up long before a drill ever comes out. Here’s why Peoria patients switch to us — and stay.")}'
               f'<div data-reveal="zoom">{carousel(us_col + them_col, "comparison", "m-carousel compare-carousel", "compare")}</div>'
               f'{section_cta(P, "compare")}</div></section>')

    steps = [("00:00", "Digital scan", "A 3D intraoral scanner captures the tooth in a few minutes. No trays, no impression putty."),
             ("00:20", "Crown design", "Software designs your crown to match your bite and the teeth beside it."),
             ("00:40", "In-office milling", "Our CEREC unit mills your crown from a solid ceramic block while you relax."),
             ("01:45", "Seat &amp; go", "We polish, check the bite and bond it in place. You leave with a permanent crown.")]
    tl = "".join(f'<div class="step" data-reveal style="--d:{i * .12:.2f}s"><span class="time">{t}</span><h4>{h}</h4><p>{p}</p></div>' for i, (t, h, p) in enumerate(steps))
    cerec = (f'<section class="section ink" id="same-day"><div class="shell"><div class="split">'
             f'<div class="split-copy left" data-reveal="left"><span class="kicker">Same-Day Technology</span>'
             f'<h2>Same-Day Crowns in Peoria, <em class="gold">Done in One Visit</em></h2>'
             f'<p>Many dental offices send a crown to an outside lab, place a temporary and ask you to return in two or three weeks. At our Peoria office, the crown is designed and milled on site — the crown you leave with is the permanent one.</p>'
             f'<p>That means no impression putty, no temporary crown coming loose over a weekend, and no second round of time off work.</p>'
             f'<div class="btn-row" style="margin-top:26px">{btn_book("Book Your Crown Appointment", "btn btn-gold btn-lg", "cerec")}{btn_call(f"Call {PHONE}", "btn btn-ghost btn-lg", "cerec")}</div></div>'
             f'<div class="split-media tilt" data-tilt="6" data-reveal="right"><video data-lazy muted loop playsinline preload="none" poster="assets/img/cerec-poster.webp" aria-label="CEREC crown being milled in our Peoria office">'
             f'<source data-src="assets/video/cerec-milling.webm" type="video/webm"><source data-src="assets/video/cerec-milling.mp4" type="video/mp4"></video>'
             f'<span class="media-badge">{ic("zap")}Milled in-office in under 15 minutes</span></div></div>'
             f'<div class="timeline">{tl}</div></div></section>')

    visit = [("Book in under a minute", "Book online or call — most new patients can be scheduled within a few days."),
             ("Fill out forms online", "Save time by completing your new patient forms before you arrive, so you see the dentist faster."),
             ("Tour &amp; conversation", "You’re greeted by our team, shown around the office and asked about your goals and concerns."),
             ("Exam, cleaning &amp; plan", "A comprehensive exam, digital X-rays and cleaning, then a written plan with costs and coverage.")]
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
        marquee(["Early Mornings from 7:30 AM", "PPO Insurance Accepted", "Same-Day Technology", "Family Owned, Not Corporate", "New Patients Welcome", f"{RATING}★ on Google"]),
        why, compare, doctors_section(P), awards_section(P), cerec, insurance_section(P),
        reviews_section(P, NP_REVIEWS, "cream"), gallery_section(P), first_visit, faq_section(P, NP_FAQ), location_section(P), final_cta(P),
        "</main>", footer(P), sticky(P)])

    return document(
        P,
        "Dentist in Peoria, AZ | Family Dentist Near Me | Belmont",
        f"Looking for the best dentist in Peoria, AZ? Belmont is a local family dentist near Arrowhead & Glendale. New patients seen within days. {RATING}★. Book online.",
        "new-patients-peoria", body, NP_FAQ, NP_REVIEWS)


# ==========================================================================
# PAGE 2 — Emergency dentist
# ==========================================================================
EM_FAQ = [
    ("Can an emergency dentist in Peoria see me today?",
     f"Very often, yes. We make every effort to see emergency patients as soon as possible and often see them the same day. Call {PHONE} as soon as the problem starts so we can get you in at the earliest opening."),
    ("Is there an emergency dentist near me open now?",
     f"Our Peoria office opens at 7:30 am Tuesday to Thursday, plus alternate Mondays and Fridays. The live status in the location section shows whether we’re open right now — call {PHONE} and our team will tell you the earliest time we can see you."),
    ("Do you do emergency tooth extractions in Peoria?",
     "Yes. When a tooth can’t be saved, emergency tooth extraction is done right here in our Peoria office. The area is thoroughly numbed first, you get clear aftercare instructions, and we can discuss options to replace the tooth once it heals."),
    ("Does a tooth extraction hurt?",
     "The area is thoroughly numbed with local anesthetic before the procedure, so you should feel pressure but not pain. Some soreness and swelling afterward is normal and usually manageable with recommended pain relief and proper aftercare."),
    ("What counts as a dental emergency?",
     "Any situation involving severe pain, uncontrolled bleeding, swelling, infection or injury to the teeth or mouth — for example a knocked-out tooth, a cracked tooth, a severe toothache or a dental abscess. When in doubt, call our office for guidance."),
    ("What should I do if I have a severe toothache?",
     "Rinse your mouth with warm water, gently floss to remove trapped food and apply a cold compress to your cheek. Take an over-the-counter pain reliever as directed and call our office promptly — toothaches often signal infection or decay that needs treatment."),
    ("What should I do if my tooth gets knocked out?",
     "Pick up the tooth by the crown, rinse it gently if dirty and try to place it back in the socket. If you can’t, store it in milk. Get to our office immediately — a tooth has the best chance of being saved when treated quickly."),
    ("Can a chipped or cracked tooth be repaired?",
     "Yes, in most cases. Depending on the damage, treatment may include bonding, a filling, a same-day CEREC crown or root canal therapy. Minor chips may only need smoothing or bonding."),
    ("What if I lose a filling or crown?",
     "Keep the piece if you can and call our office. Avoid chewing on that side and clean the area gently. A temporary dental cement from a pharmacy may offer short-term protection until you can be seen."),
    ("Will emergency dental treatment hurt?",
     "Our priority is relieving your pain. We use effective local anesthesia to keep you comfortable, explain each step before we begin, and sedation options may be available for anxious patients."),
    ("How much does an emergency dental visit cost?",
     "It depends on the exam, any X-rays needed and the treatment. We check your insurance benefits and explain costs before treatment, and patients without insurance can use the Belmont Dental Plan or CareCredit financing."),
]

EM_REVIEWS = ["joe", "tammy", "graden", "patricia", "mary", "shirley", "sayla", "chris"]


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
      <p class="hero-eyebrow">Emergency Dental Care <span class="dot"></span> Peoria, AZ</p>
      <h1>Emergency Dentist in Peoria. <em>Fast Pain Relief.</em></h1>
      <p class="hero-lead">Severe toothache, a broken tooth, swelling or a tooth that needs to come out? We make every effort to <strong>see emergency patients the same day</strong> — call now and we’ll get you in at the earliest opening. New patients welcome, most PPO plans accepted.</p>
      <div class="hero-ctas">
        {btn_call(f"Call Now {PHONE}", "btn btn-red btn-lg btn-pulse", "hero")}
        {btn_book("Book Online", "btn btn-ghost btn-lg", "hero")}
      </div>
      <p class="hero-micro">Calling is the fastest way in — we prioritize emergency cases.</p>
      <ul class="chips">
        <li>{ic("zap")}Same-day emergency visits</li>
        <li>{ic("tooth")}Emergency extractions</li>
        <li>{ic("users")}New patients welcome</li>
        <li>{ic("clock")}Open from 7:30 am</li>
      </ul>
    </div>
    <aside class="hero-card" aria-label="Tell us what's wrong" data-reveal="right">
      <span class="card-badge red">{ic("siren")}Fast Pain Relief</span>
      <h2>What’s Going On?</h2>
      <p class="sub">Tap your problem to call our Peoria team directly.</p>
      <div class="triage">{tri}</div>
      {btn_call(f"Call {PHONE}", "btn btn-red btn-lg btn-block btn-pulse", "hero-card")}
      <p class="fine">or <a {BOOK} data-cta="hero-card">book online</a> — same-day slots when available</p>
    </aside>
  </div>
  <span class="scroll-cue" aria-hidden="true"></span>
</section>"""

    st = stats([("Same Day", "Emergency visits"), (f'{RATING}<span class="gold-text">★</span>', f"{REVIEW_COUNT} Google reviews"),
                ("7:30 am", "Early opening"), ("All Ages", "Kids, adults &amp; seniors")])

    conds = [
        ("flame", "Severe Toothache", "Throbbing pain that won’t ease up or keeps you awake — we find the cause and stop it.", ""),
        ("droplet", "Abscess &amp; Infection", "Swelling, pressure, a bad taste or a pimple on the gum. Infections need prompt care.", "Urgent"),
        ("broken", "Cracked or Broken Tooth", "From a small chip to a fractured tooth — often repaired with bonding or a same-day crown.", ""),
        ("tooth", "Lost Filling or Crown", "An exposed tooth is sensitive and at risk. Bring the crown with you if you have it.", ""),
        ("alert", "Knocked-Out Tooth", "Keep it moist and call immediately — quick action gives the best chance to save it.", "Minutes matter"),
        ("zap", "Emergency Tooth Extraction", "When a tooth can’t be saved, we remove it gently right here — often the same day you call.", ""),
        ("smile", "Broken Dentures or Appliances", "Cracked dentures, partials or appliances repaired or replaced so you can eat and smile again.", ""),
        ("heart", "Gum Swelling &amp; Pain", "Sudden gum swelling, bleeding or tenderness evaluated and treated quickly.", ""),
    ]
    cc = "".join(f'<article class="cond tilt" data-tilt="6" data-reveal style="--d:{(i % 4) * .08:.2f}s">'
                 f'{f"<span class=urgent-tag>{u}</span>" if u else ""}<span class="icon-badge red">{ic(icn)}</span><h3>{t}</h3><p>{d}</p>'
                 f'<a class="call-link" {CALL} data-cta="condition">{ic("phone")}Call about this</a></article>'
                 for i, (icn, t, d, u) in enumerate(conds))
    conditions = (f'<section class="section" id="emergencies"><div class="shell">'
                  f'{head_block("Emergency Dental Services", "Fast Relief for <em class=\"gold\">Every Dental Emergency</em>", "Searching for an emergency dentist near me? If you’re in pain, bleeding, swollen or have damaged a tooth, call our Peoria emergency dental clinic — we’ll tell you exactly what to do next.")}'
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
                 f'{head_block("Before You Get Here", "What to Do <em class=\"gold\">Right Now</em>", "These steps from our Peoria team can protect your tooth and ease the pain while you’re on your way.")}'
                 f'<div class="carousel m-carousel cols-3" data-carousel><div class="carousel-track">{ac}</div>'
                 f'<div class="carousel-nav"><button class="carousel-btn" data-prev aria-label="Previous tip">{ic("left")}</button><div class="dots"></div><button class="carousel-btn" data-next aria-label="Next tip">{ic("right")}</button></div></div>'
                 f'{section_cta(P, "first-aid")}</div></section>')

    tx = [("Emergency tooth extraction", "Done right here when a tooth can’t be saved — thoroughly numbed, with clear aftercare."),
          ("Emergency root canal therapy", "Removes the infection that causes throbbing pain, and saves the tooth."),
          ("Same-day CEREC crowns", "A broken tooth restored with a permanent crown in about two hours."),
          ("Incision &amp; drainage", "Fast relief from the pressure and swelling of a dental abscess."),
          ("Pulpotomies for kids", "Relieves nerve pain in children’s teeth while saving the tooth."),
          ("Lost crowns, bonding &amp; fillings", "Lost crowns, chips and fillings repaired to stop sensitivity fast.")]
    tlist = "".join(f'<li><span class="tick">{ic("check")}</span><div><strong>{t}</strong><span>{d}</span></div></li>' for t, d in tx)
    treatments = (f'<section class="section ink" id="services"><div class="shell"><div class="split">'
                  f'<div class="split-copy left" data-reveal="left"><span class="kicker">Emergency Treatment</span>'
                  f'<h2>We Don’t Just Numb It. <em class="gold">We Fix It.</em></h2>'
                  f'<p>Relief is the first step, not the whole job. Most emergency dental care is completed right here in our Peoria office, often in the same visit — from emergency tooth extraction to a same-day crown.</p>'
                  f'<ul class="checklist">{tlist}</ul>'
                  f'<div class="btn-row">{btn_call(f"Call Now {PHONE}", "btn btn-red btn-lg btn-pulse", "treatments")}{btn_book("Book Online", "btn btn-ghost btn-lg", "treatments")}</div></div>'
                  f'<div class="split-media tilt" data-tilt="6" data-reveal="right"><video data-lazy muted loop playsinline preload="none" poster="assets/img/cerec-poster.webp" aria-label="Same-day crown being milled in our Peoria office">'
                  f'<source data-src="assets/video/cerec-milling.webm" type="video/webm"><source data-src="assets/video/cerec-milling.mp4" type="video/mp4"></video>'
                  f'<span class="media-badge">{ic("zap")}Same-day crown, milled in-office</span></div></div></div></section>')

    proc = [("Call our office", "Tell us what’s happening and how severe it is. We give you guidance and arrange the earliest visit."),
            ("Quick check-in", "We briefly review your health history, medications and allergies so your care is safe."),
            ("Focused exam &amp; X-rays", "We examine the area and take X-rays to find the cause — a crack, an infection or hidden damage."),
            ("Pain relief first", "Effective local anesthesia keeps you comfortable, and we explain each step before we begin."),
            ("Treating the problem", "A filling, bonding, a crown, root canal therapy or an extraction — we fix the immediate concern."),
            ("Aftercare &amp; follow-up", "Clear home-care instructions, and a follow-up plan when more treatment is needed.")]
    pc = "".join(f'<article class="step-card tilt" data-tilt="6" data-reveal style="--d:{(i % 3) * .1:.1f}s"><h3>{h}</h3><p>{p}</p></article>' for i, (h, p) in enumerate(proc))
    process = (f'<section class="section" id="process"><div class="shell">'
               f'{head_block("Your Emergency Visit", "What Happens <em class=\"gold\">When You Arrive</em>", "An emergency appointment focuses on understanding the problem quickly and getting you relief — while protecting your long-term oral health.")}'
               f'<div class="carousel m-carousel cols-3 steps" data-carousel data-auto><div class="carousel-track">{pc}</div>'
               f'<div class="carousel-nav"><button class="carousel-btn" data-prev aria-label="Previous step">{ic("left")}</button><div class="dots"></div><button class="carousel-btn" data-next aria-label="Next step">{ic("right")}</button></div></div>'
               f'{section_cta(P, "process")}</div></section>')

    why = usp_section(P,
        [("zap", "Seen fast — often today", "We prioritize emergency cases and make every effort to see you the same day you call."),
         ("clock", "Early hours", "Open from 7:30 am Tuesday to Thursday, plus alternate Mondays and Fridays."),
         ("tooth", "Most treatment in-house", "Emergency extractions, root canals and same-day CEREC crowns — handled here, not referred out.")],
        [("scan", "Answers you can see", "Digital X-rays and 3D CBCT imaging show exactly what’s wrong — on screen, explained in plain language."),
         ("headphones", "Pain relief first", "Effective local anesthesia, headphones and blankets — with sedation options for anxious patients."),
         ("shield", "Costs before treatment", "We check your insurance and explain costs up front. No surprise bills at checkout.")],
        "Why Peoria Calls Belmont <em class=\"gold\">First</em>",
        "A family-owned Peoria emergency dental clinic with the technology to fix most dental emergencies in one visit — and a team that genuinely cares.",
        "img-belmont-dentistry-front-desk-reception-area.webp")

    offers = offers_section(P, [
        ("Fast Access", "Same-Day Emergency Visits", "Emergency cases prioritized",
         "Call as soon as symptoms start — we make every effort to see you the same day, and new patients are always welcome.",
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
        "Getting out of pain shouldn’t be complicated. Here’s how we make emergency dental care in Peoria fast, comfortable and affordable.")

    body = "\n".join([
        topbar(P), site_header(P), "<main>", hero, st, conditions,
        marquee(["Emergency Dental Care", "Emergency Tooth Extraction", "Emergency Root Canals", "Same-Day CEREC Crowns", "Most PPO Plans Accepted", "Open from 7:30 AM"], red=True),
        first_aid, treatments, process, reviews_section(P, EM_REVIEWS, "cream"), why, offers, doctors_section(P),
        awards_section(P), insurance_section(P), gallery_section(P, "cream"), faq_section(P, EM_FAQ), location_section(P), final_cta(P),
        "</main>", footer(P), sticky(P)])

    return document(
        P,
        "Emergency Dentist Peoria, AZ | Same-Day Care | Belmont",
        f"Need an emergency dentist in Peoria, AZ? Same-day emergency dental care & emergency tooth extraction near you. {RATING}★ on Google. Call {PHONE} now.",
        "emergency-dentist-peoria", body, EM_FAQ, EM_REVIEWS, theme="#1E1B16")


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
  window.dataLayer.push({ event: 'thank_you_view', lp_page: 'thank-you-peoria', lp_source: src });
})();
</script>
"""


def page_thank_you():
    P = "ty"
    hero = f"""
<section class="hero ty-hero" id="hero">
  <div class="hero-media"><img src="assets/img/img-belmont-dentistry-patient-waiting-room.webp" alt="" width="960" height="640" fetchpriority="high"></div>
  <img class="hero-watermark" src="assets/img/logo_watermark.svg" alt="" aria-hidden="true">
  <div class="shell">
    <div class="ty-check" aria-hidden="true"><svg viewBox="0 0 52 52"><circle cx="26" cy="26" r="24"/><path d="M15 27l7 7 15-16"/></svg></div>
    <p class="hero-eyebrow">Belmont Dentistry Peoria <span class="dot"></span> Request Received</p>
    <h1>Thank You! <em>We’ll See You Soon.</em></h1>
    <p class="hero-lead">Your request has been sent to our Peoria team. You’ll get a confirmation by text or email shortly — and if anything needs a quick check, we’ll call you from <strong>{PHONE}</strong>.</p>
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
         f'<a class="btn btn-dark btn-block" href="{SITE}/peoria-az/patient-forms/" target="_blank" rel="noopener" data-cta="forms">{ic("file")}<span>Patient Forms</span></a>'),
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
                  f'<div class="er-warning ty-help" data-reveal>{ic("siren")}<p><strong>Need to reschedule, or in pain before your appointment?</strong> Call {PHONE} — we make every effort to see dental emergencies the same day.</p>'
                  f'<a class="btn btn-red btn-pulse" {CALL} data-cta="ty-help">{ic("phone", "ring-icon")}<span>Call Now</span></a></div>'
                  f'</div></section>')

    team = "".join(f'<article class="team-mini" data-reveal style="--d:{i * .1:.1f}s"><img src="{img}" alt="{full_name(n, s)}" width="467" height="611" loading="lazy">'
                   f'<h3>{full_name(n, s)}</h3><span>{r} · {c.split(" · ")[-1] if c.startswith("DDS") else c.split(" · ")[0]}</span></article>'
                   for i, (n, s, r, c, img, *_rest) in enumerate(DOCTORS))
    comfort = "".join(f"<li>{ic(i)}{t}</li>" for i, t in [("headphones", "Noise-cancelling headphones"), ("monitor", "TVs in every room"), ("blanket", "Warm blankets"),
                                                         ("coffee", "Complimentary beverages"), ("droplet", "Nitrous &amp; oral sedation"), ("heart", "A team that listens")])
    dentists = (f'<section class="section ink" id="dentists"><div class="shell">'
                f'{head_block("You’re in Good Hands", "Meet the Team <em class=\"gold\">Caring for You</em>", f"A family-owned Peoria practice rated {RATING}★ by {REVIEW_COUNT} Google reviewers. Here’s who you’ll meet.")}'
                f'<div class="team-grid">{team}</div>'
                f'<h3 class="ty-sub" data-reveal>Your comfort menu — included at every visit</h3><ul class="perks dark" data-reveal>{comfort}</ul>'
                f'<div class="section-cta" data-reveal><a class="btn btn-gold btn-lg" href="{GMB_URL}" target="_blank" rel="noopener" data-cta="dentists">{ic("star")}<span>{two(f"Read Our {REVIEW_COUNT} Reviews", "Our Reviews")}</span></a>'
                f'{btn_call(two(f"Call {PHONE}", "Call Us"), "btn btn-ghost btn-lg", "dentists")}</div></div></section>')

    body = "\n".join([site_header(P), "<main>", hero, next_steps, dentists, location_section(P), "</main>", footer(P), sticky(P)])
    return document(
        P,
        "Thank You | Belmont Dentistry Peoria",
        "Thank you for choosing Belmont Dentistry Peoria. Here’s what happens next, what to bring and how to find our office at 7966 W Thunderbird Rd, Suite 101.",
        "thank-you-peoria", body, None, None, robots="noindex, nofollow", head_extra=TY_DATALAYER)


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
        "new-patients-peoria.html": page_new_patients(),
        "emergency-dentist-peoria.html": page_emergency(),
        "thank-you-peoria.html": page_thank_you(),
    }
    (HERE / "standalone").mkdir(exist_ok=True)
    for name, doc in pages.items():
        (HERE / name).write_text(doc, encoding="utf-8")
        size = bundle(HERE / name, HERE / "standalone" / name)
        print(f"wrote {name} ({len(doc) / 1024:.0f} KB) + standalone/{name} ({size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
