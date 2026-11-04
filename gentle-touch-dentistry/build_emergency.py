#!/usr/bin/env python3
"""Builds emergency-dentist.html from general-new-patient.html.

The emergency page reuses the general page's approved design system (CSS,
icon sprite, behaviour script) and several shared sections (credentials,
doctors, gallery, reviews, insurance, contact), and adds emergency-specific
sections around them. Re-run after editing the general page:

    python3 build_emergency.py
"""
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = (HERE / "general-new-patient.html").read_text(encoding="utf-8")
OUT = HERE / "emergency-dentist.html"

BOOK = "https://book.allinone.dental/gentle?referrer_id=3"
TEL = "tel:+14693363069"
PHONE = "(469) 336-3069"
GBP = "https://maps.app.goo.gl/3b5hkvUb6ybnhUne9"
IMG = "https://mygentletouchdentistry.com/images/"
STARS = '<svg><use href="#i-star"/></svg>' * 5


def between(text, start, end, include_start=True):
    i = text.index(start)
    j = text.index(end, i + len(start))
    return text[i if include_start else i + len(start):j]


def section(marker):
    """Return a shared section block, from its comment marker to its closing tag."""
    i = SRC.index(f"<!-- ============ {marker} ============ -->")
    j = SRC.index("</section>", i) + len("</section>")
    return SRC[i:j]


def sub(text, old, new, count=1):
    assert text.count(old) == count, (old[:70], text.count(old))
    return text.replace(old, new)


# --------------------------------------------------------------- shared parts
style = between(SRC, "<style>", "</style>", include_start=False)
sprite = between(SRC, "<!-- Icon sprite -->", '<div class="progress"')
script = SRC[SRC.rindex("<script>"):SRC.rindex("</script>") + len("</script>")]

# Extra icons for the emergency page (Font Awesome paths, already used in this repo)
legacy = (HERE.parent / "emergency-dentist-en.html").read_text(encoding="utf-8")
extra = "".join(re.search(rf'<symbol id="{n}".*?</symbol>', legacy).group(0)
                for n in ("i-warning", "i-hospital", "i-drop", "i-kit"))
sprite = sprite.replace("</svg>", extra + "</svg>", 1)

script = sub(script, "lp:'gentle-touch-general-new-patient'", "lp:'gentle-touch-emergency'")

# ------------------------------------------------------- emergency-only CSS
style += r"""
/* =====================================================================
   EMERGENCY PAGE ADDITIONS
   ===================================================================== */
.topbar,.header{overflow-x:clip}
:root{--urgent:#e5484d;--urgent-deep:#c33236;--urgent-soft:#fdeeee}
.dot-urgent{display:inline-block;width:9px;height:9px;border-radius:50%;background:var(--urgent);position:relative;flex:none}
.dot-urgent::after{content:"";position:absolute;inset:-4px;border-radius:50%;border:2px solid var(--urgent);animation:ring 1.6s infinite}
.pill .dot.red{background:var(--urgent-soft);color:var(--urgent)}
.h-live{display:none;flex-direction:column;line-height:1.2;text-align:right}
.h-live small{font-size:12px;color:var(--urgent);font-weight:800;text-transform:uppercase;letter-spacing:.06em;display:flex;align-items:center;gap:6px;justify-content:flex-end}
.h-live strong{font-family:var(--f-display);font-size:14px;color:var(--ink)}
.h-call-d{display:none !important}

/* hero live status */
.live-hero{display:inline-flex;align-items:center;gap:10px;margin:4px 0 18px;padding:9px 16px;border-radius:var(--pill);background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.22);font-weight:700;font-size:14.5px;color:#fff;backdrop-filter:blur(6px)}
.live-hero i{width:10px;height:10px;border-radius:50%;background:#ffb547;position:relative;flex:none}
.live-hero.is-open i{background:#3ddc97}
.live-hero.is-open i::after{content:"";position:absolute;inset:-4px;border-radius:50%;border:2px solid #3ddc97;animation:ring 1.8s infinite}
.hero-copy .live-hero{order:2}
.btn-urgent{background:var(--brand);color:#fff;box-shadow:0 14px 34px rgba(31,78,140,.55)}
.btn-urgent:hover{background:var(--sky);color:var(--ink)}
.hero .btn-urgent{background:#fff;color:var(--ink);box-shadow:0 14px 34px rgba(0,0,0,.3)}
.hero .btn-urgent:hover{background:var(--sky)}
.hero .btn-urgent.btn-pulse::before{border-color:#fff}
.hero .hero-card .btn-urgent{background:var(--brand);color:#fff;box-shadow:0 12px 28px rgba(31,78,140,.4)}
.hero .hero-card .btn-urgent:hover{background:var(--ink)}
.hero .hero-card .btn-urgent.btn-pulse::before{border-color:var(--brand)}

/* conditions grid */
.cond{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}
.cond-card{position:relative;background:#fff;border:1px solid #e3edf6;border-radius:var(--r);padding:22px 16px;text-align:center;box-shadow:var(--sh-sm);transition:transform .45s var(--ease),box-shadow .45s,border-color .3s}
.cond-card:hover{transform:translateY(-6px);box-shadow:var(--sh);border-color:#f3c4c5}
.cond-card .c-ico{width:54px;height:54px;margin:0 auto 12px;border-radius:16px;background:var(--urgent-soft);color:var(--urgent);display:grid;place-items:center;transition:transform .45s var(--ease)}
.cond-card:hover .c-ico{transform:rotate(-8deg) scale(1.08)}
.cond-card .c-ico svg{width:24px;height:24px;fill:currentColor}
.cond-card h3{font-size:16.5px;margin-bottom:4px;line-height:1.25}
.cond-card p{font-size:13.5px;color:var(--slate);margin:0;line-height:1.45}
.cond-card .urg{position:absolute;top:10px;right:10px;font-size:10px;font-weight:800;letter-spacing:.06em;text-transform:uppercase;color:var(--urgent);background:var(--urgent-soft);padding:3px 8px;border-radius:var(--pill)}

/* first aid */
.aid{display:grid;gap:14px}
.aid-card{position:relative;background:#fff;border-radius:var(--r);padding:24px 22px;border:1px solid #e3edf6;box-shadow:var(--sh-sm);transition:transform .45s var(--ease),box-shadow .45s}
.aid-card:hover{transform:translateY(-5px);box-shadow:var(--sh)}
.aid-card .n{display:inline-grid;place-items:center;width:40px;height:40px;border-radius:12px;background:linear-gradient(135deg,var(--sky),var(--brand));color:#fff;font-family:var(--f-display);font-weight:800;margin-bottom:12px}
.aid-card h3{font-size:18.5px;margin-bottom:6px}
.aid-card p{font-size:15px;color:var(--slate);margin:0}
.aid-card .tip{display:inline-block;margin-top:10px;font-size:12.5px;font-weight:800;color:var(--urgent);background:var(--urgent-soft);padding:4px 10px;border-radius:var(--pill)}
.er{margin-top:24px;display:grid;gap:16px;align-items:center;background:var(--urgent-soft);border:1.5px solid #f3c4c5;border-radius:var(--r-lg);padding:24px 22px}
.er .er-ico{width:56px;height:56px;border-radius:16px;background:var(--urgent);color:#fff;display:grid;place-items:center;flex:none}
.er .er-ico svg{width:26px;height:26px;fill:currentColor}
.er h3{font-size:20px;margin-bottom:4px;color:var(--urgent-deep)}
.er p{margin:0;color:#6d3b3c;font-size:15px}
.er .btn{background:var(--urgent);color:#fff;box-shadow:0 10px 24px rgba(229,72,77,.35)}
.er .btn:hover{background:var(--urgent-deep)}

/* visit steps (5) */
.steps.five .step h3{font-size:18px}

@media (min-width:640px){
  .cond{grid-template-columns:repeat(3,1fr)}
  .aid{grid-template-columns:repeat(2,1fr)}
}
@media (min-width:1024px){
  .h-live{display:flex}
  .h-call-d{display:inline-flex !important}
  .h-book{display:none !important}
  .cond{grid-template-columns:repeat(5,1fr);gap:16px}
  .aid{grid-template-columns:repeat(3,1fr);gap:18px}
  .er{grid-template-columns:auto 1fr auto;padding:26px 30px;gap:22px}
  .steps.five{grid-template-columns:repeat(5,1fr);gap:16px}
  .steps.five::before{left:8%;right:8%}
  .steps.five .step{padding:80px 16px 24px}
  .hero h1{font-size:clamp(44px,4.1vw,60px);text-wrap:balance}
  .hero-copy .live-hero{order:3}
  .hero-copy .cta-row{order:4;margin-bottom:22px}
  .hero-copy .rotator{order:5}
  .hero-copy .hero-sub{order:6}
  .hero-copy .hero-points{order:7}
  .hero-copy .hero-trust{order:8;margin-top:4px}
}
@media (max-width:767px){
  .live-hero{font-size:13.5px;padding:8px 14px}
  .cond-card{padding:20px 12px}
  .aid-card{text-align:center}
  .er{text-align:center;justify-items:center}
  .er .btn{width:100%}
  .mbar{grid-template-columns:1.35fr 1fr}
  .mbar .rate{color:var(--ink);font-weight:700}
}
"""

# ------------------------------------------------------------ head + schema
head = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Emergency Dentist Richardson, TX | Same-Day Emergency Dental Care | Gentle Touch Dentistry</title>
<meta name="description" content="Need an emergency dentist in Richardson, TX? Same-day emergency dental care whenever possible for toothaches, broken teeth, abscesses &amp; emergency tooth extractions. Insured or not, 5.0 stars from 107 reviews. Call {PHONE}.">
<meta name="robots" content="noindex, nofollow">
<meta name="theme-color" content="#1f4e8c">
<link rel="icon" href="https://mygentletouchdentistry.com/icon-192.png" type="image/png">
<link rel="apple-touch-icon" href="https://mygentletouchdentistry.com/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="preconnect" href="https://mygentletouchdentistry.com">
<link rel="preload" as="image" href="{IMG}img-video-thumb-banner.jpg">
<link href="https://fonts.googleapis.com/css2?family=Figtree:wght@400;500;600;700&family=Fraunces:ital,opsz,wght@1,9..144,500;1,9..144,600&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap" rel="stylesheet">
"""

# Practice schema is identical to the general page; FAQ schema is emergency-specific.
practice_schema = SRC[SRC.index('<script type="application/ld+json">'):SRC.index("</script>") + len("</script>")]
practice_schema = sub(practice_schema, '"medicalSpecialty": ["Dentistry", "Periodontics", "CosmeticDentistry"],',
                      '"medicalSpecialty": ["Dentistry", "Periodontics", "CosmeticDentistry"],\n  "availableService": [\n    {"@type": "MedicalProcedure", "name": "Emergency dental care"},\n    {"@type": "MedicalProcedure", "name": "Emergency tooth extraction"},\n    {"@type": "MedicalProcedure", "name": "Emergency root canal therapy"},\n    {"@type": "MedicalProcedure", "name": "Same-day CEREC crowns"}\n  ],')

FAQ = [
    ("Do you offer same-day emergency dental appointments in Richardson?",
     f"Yes. Gentle Touch Dentistry Richardson offers same-day emergency appointments whenever possible. Please call {PHONE} first so our team can review your symptoms, give you first-aid advice and reserve the soonest opening.",
     f'Yes. Gentle Touch Dentistry offers same-day emergency appointments whenever possible. Please call <a href="{TEL}">{PHONE}</a> first so our team can review your symptoms, give you first-aid advice and reserve the soonest opening for you.'),
    ("What counts as a dental emergency?",
     "A dental emergency is any problem that needs prompt care to relieve severe pain, stop an infection or save a tooth — for example a knocked-out or loose tooth, a cracked or broken tooth, a severe toothache, an abscess or facial swelling, a lost filling or crown, or an injury to the gums, lips or tongue.",
     "A dental emergency is any problem that needs prompt care to relieve severe pain, stop an infection or save a tooth — for example a knocked-out or loose tooth, a cracked or broken tooth, a severe toothache, an abscess or facial swelling, a lost filling or crown, or an injury to the gums, lips or tongue. Not sure? Call us and we'll help you decide."),
    ("I don't have dental insurance. Can I still see an emergency dentist?",
     "Absolutely. We provide emergency dental care for adults without insurance. You'll get a clear cost estimate before any treatment begins, and our in-office membership plan gives you immediate benefits and 12 months of coverage starting the day you enroll.",
     f'Absolutely — we provide emergency dental care for adults without insurance. You\'ll get a clear cost estimate before any treatment begins, and our in-office membership plan gives you immediate benefits and 12 months of coverage starting the day you enroll. <a href="{TEL}">Call us</a> and we\'ll explain your options.'),
    ("Do you offer emergency tooth extractions?",
     "Yes. When a tooth is too damaged or infected to save, we can remove it gently and talk you through replacement options such as implants or bridges. We always explain whether the tooth can be saved first, for example with root canal therapy or a crown.",
     "Yes. When a tooth is too damaged or infected to save, our team — including Dr. Kolli, who focuses on surgical dentistry such as wisdom tooth removal — can remove it gently and talk you through replacement options like implants or bridges. We always tell you first whether the tooth can be saved with root canal therapy or a crown."),
    ("What should I do if my tooth gets knocked out?",
     "Pick the tooth up by the crown, not the root, and rinse it gently if it's dirty. Try to place it back in the socket, or keep it moist in milk. Call an emergency dentist right away — being seen within about 30–60 minutes gives the best chance of saving the tooth.",
     f'Pick the tooth up by the crown, not the root, and rinse it gently if it\'s dirty. Try to place it back in the socket, or keep it moist in milk. Call <a href="{TEL}">{PHONE}</a> right away — being seen within about 30–60 minutes gives the best chance of saving the tooth.'),
    ("Should I go to the ER or the dentist for a toothache?",
     "For most toothaches, a dentist is the right choice because we can treat the cause, such as an infection or cracked tooth. Go to the ER or call 911 if you have swelling that affects breathing or swallowing, uncontrolled bleeding, a possible broken jaw, or a high fever with facial swelling.",
     "For most toothaches, a dentist is the right choice because we can treat the cause, such as an infection or a cracked tooth. Go to the ER or call 911 if you have swelling that affects breathing or swallowing, uncontrolled bleeding, a possible broken jaw, or a high fever with facial swelling."),
    ("What are your hours for emergency dental care?",
     "We're open Monday 8–5, Wednesday 10–6:30, Thursday 10–4, Friday 7–4:30 and Saturday 10–2 by appointment only. We're closed Tuesday and Sunday. We offer same-day emergency appointments whenever possible during these hours, so please call first.",
     "We're open Monday 8–5, Wednesday 10–6:30, Thursday 10–4, Friday 7–4:30 and Saturday 10–2 by appointment only. We're closed Tuesday and Sunday. We offer same-day emergency appointments whenever possible during these hours — please call first. For life-threatening emergencies, call 911."),
    ("Does insurance cover emergency dental visits?",
     "Many dental plans cover emergency exams and X-rays, plus part of the treatment you need. We're in-network with 29+ PPO plans including Aetna, Cigna, Delta Dental, MetLife and United Healthcare, and we verify your benefits for you.",
     "Many dental plans cover emergency exams and X-rays, plus part of the treatment you need. We're in-network with 29+ PPO plans including Aetna, Cigna, Delta Dental, MetLife and United Healthcare, and our coordinator verifies your benefits and files the claim for you."),
    ("How can I relieve tooth pain until my appointment?",
     "Rinse with warm salt water, gently floss to remove trapped food, and apply a cold compress to the outside of your cheek. An over-the-counter pain reliever may help when taken as directed. Never place aspirin directly on your gums.",
     "Rinse with warm salt water, gently floss to remove trapped food, and apply a cold compress to the outside of your cheek. An over-the-counter pain reliever may help when taken as directed. Never place aspirin directly on your gums — and call us so we can see you as soon as possible."),
]


def json_str(s):
    return s.replace("\\", "\\\\").replace('"', '\\"')


faq_schema = ('<script type="application/ld+json">\n{\n  "@context": "https://schema.org",\n  "@type": "FAQPage",\n  "mainEntity": [\n'
              + ",\n".join(f'    {{ "@type": "Question", "name": "{json_str(q)}",\n      "acceptedAnswer": {{ "@type": "Answer", "text": "{json_str(a)}" }} }}'
                           for q, a, _ in FAQ)
              + "\n  ]\n}\n</script>")

# ------------------------------------------------------------------ chrome
topbar = f"""<div class="topbar">
  <div class="shell">
    <div class="t-left">
      <span><span class="dot-urgent" aria-hidden="true"></span>Same-day emergency appointments</span>
      <span class="hide-m"><svg class="ico"><use href="#i-pin"/></svg>1750 Alma Rd #110, Richardson, TX</span>
    </div>
    <div class="t-right">
      <span class="live hide-m" data-live><i></i><b data-live-text>Office hours</b></span>
      <a class="hide-m" href="{TEL}"><span><svg class="ico"><use href="#i-phone"/></svg>{PHONE}</span></a>
    </div>
  </div>
</div>"""

header = f"""<header class="header" id="top">
  <div class="shell">
    <span class="brand"><img src="{IMG}gentle-touch-dentistry-richardson-logo.webp" width="240" height="75" alt="Gentle Touch Dentistry — Emergency Dentist in Richardson, TX"></span>
    <div class="h-actions">
      <span class="h-rating"><svg class="g-logo"><use href="#g"/></svg><span><b>5.0</b> <span class="stars" aria-hidden="true">{STARS}</span><br>107 Google reviews</span></span>
      <span class="h-live"><small><span class="dot-urgent" aria-hidden="true"></span>Dental emergency?</small><strong data-live-text>Same-day appointments</strong></span>
      <a class="btn btn-urgent btn-pulse btn-shine h-call-d" href="{TEL}"><svg class="ico phone-ico"><use href="#i-phone"/></svg>Call {PHONE}</a>
      <a class="btn btn-call h-call-m" href="{TEL}" aria-label="Call {PHONE}"><svg class="ico phone-ico"><use href="#i-phone"/></svg><span>Call</span></a>
    </div>
  </div>
</header>"""

# -------------------------------------------------------------------- hero
hero = f"""<!-- ============ HERO ============ -->
<section class="hero" id="hero">
  <video muted loop playsinline preload="none" aria-hidden="true" poster="{IMG}img-video-thumb-banner.jpg"
         data-src-desktop="https://mygentletouchdentistry.com/videos/hero-desktop.mp4"
         data-src-mobile="https://mygentletouchdentistry.com/videos/hero-mobile.mp4"></video>
  <div class="shell">
    <div class="hero-grid">
      <div class="hero-copy">
        <span class="pill h-pill rv" itemscope itemtype="https://schema.org/Dentist" itemid="https://mygentletouchdentistry.com/#practice">
          <span class="dot red"><svg><use href="#i-bolt"/></svg></span>
          <meta itemprop="name" content="Gentle Touch Dentistry Richardson">
          <meta itemprop="telephone" content="+1-469-336-3069">
          <span itemprop="aggregateRating" itemscope itemtype="https://schema.org/AggregateRating">
            Emergency <span class="long">Dentist in Richardson, TX</span> &middot; <b itemprop="ratingValue">5.0</b><meta itemprop="bestRating" content="5"><meta itemprop="reviewCount" content="107">
          </span>
          <span class="stars" aria-hidden="true">{STARS}</span>
        </span>

        <h1 class="rv" data-d="1"><span class="acc">Same-Day<svg viewBox="0 0 300 20" preserveAspectRatio="none" aria-hidden="true"><path d="M4 14 C 80 4, 200 2, 296 10"/></svg></span> Emergency Dentist in Richardson, TX</h1>
        <p class="tagline rv" data-d="2">In pain? We'll make room for you today.</p>
        <span class="live-hero rv" data-d="2" data-live><i></i><span data-live-text>Call now for the soonest opening</span></span>

        <div class="rotator rv" data-d="2" aria-live="off">
          <span>Fast relief for</span>
          <span class="word" data-rotate><span class="on">Severe Toothaches</span><span>Broken &amp; Cracked Teeth</span><span>Knocked-Out Teeth</span><span>Abscess &amp; Swelling</span><span>Lost Crowns &amp; Fillings</span><span>Emergency Extractions</span></span>
        </div>

        <p class="hero-sub rv" data-d="3">Toothache, broken tooth or swelling? <strong>Gentle Touch Dentistry</strong> provides <strong>emergency dental care in Richardson</strong> with same-day appointments whenever possible. Searching for an <strong>emergency dentist near me</strong>? Call now — insured or not, we're here to help.</p>

        <ul class="hero-points rv" data-d="3">
          <li><svg class="ico"><use href="#i-check"/></svg>Same-day emergency visits whenever possible</li>
          <li><svg class="ico"><use href="#i-check"/></svg>No insurance? Upfront pricing &amp; membership plan</li>
          <li><svg class="ico"><use href="#i-check"/></svg>Numbing, nitrous &amp; oral sedation for comfort</li>
        </ul>

        <div class="cta-row rv" data-d="4">
          <a class="btn btn-urgent btn-xl btn-pulse" href="{TEL}"><svg class="ico phone-ico"><use href="#i-phone"/></svg>Call {PHONE}</a>
          <a class="btn btn-primary btn-xl btn-shine" href="{BOOK}" target="_blank" rel="noopener"><svg class="ico"><use href="#i-cal"/></svg>Book My Slot For Today</a>
        </div>

        <div class="hero-trust rv" data-d="5">
          <a class="g-badge" href="{GBP}" target="_blank" rel="noopener" aria-label="Rated 5.0 out of 5 from 107 Google reviews">
            <span class="g-ico"><svg class="g-logo"><use href="#g"/></svg></span>
            <span><b>5.0</b> <span class="stars" aria-hidden="true">{STARS}</span><small>107 Google reviews</small></span>
          </a>
          <div class="avatars" aria-hidden="true">
            <img src="{IMG}dr-anuritha-chepyala.jpg" alt="" width="38" height="38">
            <img src="{IMG}img-dr-Nauman.jpg" alt="" width="38" height="38">
            <img src="{IMG}img-dr-kolli.webp" alt="" width="38" height="38">
          </div>
          <div class="txt"><b>3 experienced doctors</b><br>Incl. a surgical-focused dentist</div>
        </div>
      </div>

      <aside class="hero-card rv rv-r" data-d="3" data-tilt aria-labelledby="hc-title">
        <span class="ribbon">Emergency Visit</span>
        <span class="float-chip c1"><span class="fi"><svg><use href="#i-bolt"/></svg></span>Same-day when possible</span>
        <span class="float-chip c2"><span class="fi"><svg><use href="#i-shield"/></svg></span>Insured or not</span>
        <h2 id="hc-title">Get Out of Pain, Fast</h2>
        <p class="lead">What happens when you call our emergency dentist in Richardson:</p>
        <ul class="inc">
          <li><span class="ck"><svg><use href="#i-check"/></svg></span>Quick phone triage &amp; first-aid advice</li>
          <li><span class="ck"><svg><use href="#i-check"/></svg></span>Fast exam with low-radiation digital X-rays</li>
          <li><span class="ck"><svg><use href="#i-check"/></svg></span>Pain relief first — numbing &amp; nitrous available</li>
          <li><span class="ck"><svg><use href="#i-check"/></svg></span>Treat or stabilize the tooth the same visit</li>
          <li><span class="ck"><svg><use href="#i-check"/></svg></span>Clear options &amp; cost estimate upfront</li>
        </ul>
        <a class="btn btn-urgent btn-block btn-pulse" href="{TEL}"><svg class="ico phone-ico"><use href="#i-phone"/></svg>Call Now — Get Seen Today</a>
        <a class="btn btn-primary btn-block btn-shine" href="{BOOK}" target="_blank" rel="noopener"><svg class="ico"><use href="#i-cal"/></svg>Book My Slot For Today</a>
        <div class="mini">
          <span><svg class="ico"><use href="#i-clock"/></svg><span data-live-text>Open Mon–Sat</span></span>
          <span><svg class="ico"><use href="#i-cal"/></svg>Saturdays by appt.</span>
        </div>
      </aside>
    </div>
  </div>
</section>"""

stats = """<!-- ============ STATS ============ -->
<section class="stats" aria-label="Practice at a glance">
  <div class="shell">
    <div class="stat rv"><div class="n"><span data-count="5" data-dec="1">5.0</span><sup>★</sup></div><div class="l">Google Rating</div><div class="s">From 107 patient reviews</div></div>
    <div class="stat rv" data-d="1"><div class="n">Same<sup>-day</sup></div><div class="l">Emergency Visits</div><div class="s">Whenever possible — call first</div></div>
    <div class="stat rv" data-d="2"><div class="n"><span data-count="29">29</span><sup>+</sup></div><div class="l">In-Network PPO Plans</div><div class="s">Plus a no-insurance plan</div></div>
    <div class="stat rv" data-d="3"><div class="n"><span data-count="2016" data-start="1990">2016</span></div><div class="l">Serving Richardson</div><div class="s">Locally owned &amp; trusted</div></div>
  </div>
</section>

<div class="marquee" aria-hidden="true">
  <div class="marquee-track">
""" + ("    " + "".join(f"<span>{t}</span>" for t in [
    "Severe Toothache", "Broken Tooth", "Knocked-Out Tooth", "Dental Abscess", "Facial Swelling",
    "Lost Crown", "Lost Filling", "Emergency Tooth Extraction", "Emergency Root Canal", "Same-Day CEREC Crowns",
    "Broken Braces Wire", "Gum &amp; Lip Injuries"]) + "\n") * 2 + """  </div>
</div>"""

# --------------------------------------------------------------- conditions
CONDS = [
    ("i-bolt", "Severe Toothache", "Throbbing pain that won't let you eat or sleep", True),
    ("i-tooth", "Chipped or Broken Tooth", "Cracks, fractures &amp; sharp edges", False),
    ("i-warning", "Knocked-Out Tooth", "Best saved within 30–60 minutes", True),
    ("i-drop", "Abscess &amp; Swelling", "Infection, gum or facial swelling", True),
    ("i-shield", "Lost Crown or Filling", "Protect the exposed tooth quickly", False),
    ("i-tooth", "Loose or Shifted Tooth", "Pushed out of alignment by injury", False),
    ("i-kit", "Gum, Lip &amp; Tongue Injuries", "Cuts &amp; soft tissue trauma", False),
    ("i-sparkle", "Broken Braces Wire", "Loose brackets, bands or poking wires", False),
    ("i-check", "Object Stuck Between Teeth", "Painful pressure you can't remove", False),
    ("i-screen", "Broken Temporary or Denture", "Problems with temporary restorations", False),
]
conditions = f"""<!-- ============ CONDITIONS ============ -->
<section class="section ivory" id="emergencies">
  <div class="shell">
    <div class="head rv">
      <span class="eyebrow">Emergency Dental Services</span>
      <h2>Is It a <em class="acc">Dental Emergency?</em></h2>
      <p>A dental emergency is any problem that needs prompt care to relieve severe pain, stop an infection or save a tooth. Our emergency dental services in Richardson cover all of these — and more.</p>
    </div>
    <div class="cond">
""" + "".join(
    f"""      <div class="cond-card rv" data-d="{i % 5}">{'<span class="urg">Urgent</span>' if urg else ''}<span class="c-ico"><svg><use href="#{ico}"/></svg></span><h3>{t}</h3><p>{d}</p></div>\n"""
    for i, (ico, t, d, urg) in enumerate(CONDS)) + f"""    </div>
    <div class="sec-cta rv">
      <p style="font-weight:700;margin-bottom:14px">Not sure if it's an emergency? Call us — we'll tell you what to do.</p>
      <div class="cta-row center">
        <a class="btn btn-urgent btn-xl btn-pulse" href="{TEL}"><svg class="ico phone-ico"><use href="#i-phone"/></svg>Call {PHONE}</a>
        <a class="btn btn-primary btn-xl btn-shine" href="{BOOK}" target="_blank" rel="noopener"><svg class="ico"><use href="#i-cal"/></svg>Book Online</a>
      </div>
    </div>
  </div>
</section>"""

# ---------------------------------------------------------- offers / payment
offers = f"""<!-- ============ OFFERS ============ -->
<section class="section" id="offers">
  <div class="shell">
    <div class="head rv">
      <span class="eyebrow">Insured or Not</span>
      <h2>Emergency Care You Can <em class="acc">Afford</em></h2>
      <p>No one should stay in pain because of cost. Whether you have insurance or need an emergency dentist near you with no insurance, we'll get you seen and explain every cost upfront.</p>
    </div>
    <div data-carousel><div class="offers mswipe track-m">
      <article class="offer featured rv" data-tilt>
        <span class="tag">Call First</span>
        <span class="o-ico"><svg><use href="#i-bolt"/></svg></span>
        <h3>Same-Day Emergency Visit</h3>
        <div class="big">Seen Today<small>Whenever possible — we reserve the soonest opening</small></div>
        <p>Exam, digital X-rays and pain relief — then we treat or stabilize the tooth so you can get back to your day.</p>
        <a class="btn btn-primary btn-block btn-shine" href="{TEL}"><svg class="ico phone-ico"><use href="#i-phone"/></svg>Call Now</a>
      </article>
      <article class="offer rv" data-d="1" data-tilt>
        <span class="o-ico"><svg><use href="#i-card"/></svg></span>
        <h3>No Insurance? You're Covered.</h3>
        <div class="big">Membership Plan<small>12 months of coverage from day one</small></div>
        <p>Emergency dental care for adults without insurance — with immediate benefits the day you enroll.</p>
        <a class="btn btn-outline btn-block" href="{TEL}">Ask About the Plan</a>
      </article>
      <article class="offer rv" data-d="2" data-tilt>
        <span class="o-ico"><svg><use href="#i-shield"/></svg></span>
        <h3>Insurance Accepted</h3>
        <div class="big">29+ PPO Plans<small>We verify &amp; file your claim</small></div>
        <p>Many plans cover emergency exams and X-rays plus part of your treatment. Aetna, Cigna, Delta Dental, MetLife &amp; more.</p>
        <a class="btn btn-outline btn-block" href="#insurance">See Accepted Plans</a>
      </article>
      <article class="offer rv" data-d="3" data-tilt>
        <span class="o-ico"><svg><use href="#i-check"/></svg></span>
        <h3>No Surprise Bills</h3>
        <div class="big">Upfront Pricing<small>Estimate before any treatment</small></div>
        <p>We explain your options and the cost of each — so you can make the right decision for your smile and budget.</p>
        <a class="btn btn-outline btn-block" href="{BOOK}" target="_blank" rel="noopener">Book My Slot</a>
      </article>
    </div>
    <div class="dots mdots" aria-hidden="true"></div></div>
    <p class="fine">Same-day appointments are subject to availability. Coverage varies by plan.</p>
  </div>
</section>"""

# --------------------------------------------------------------- treatments
def panel(pid, tid, img, alt, w, h, badge_ico, badge, title, intro, items, cta, on=False):
    lis = "".join(f'<li><span class="ck"><svg><use href="#i-check"/></svg></span><div><b>{b}</b><span>{s}</span></div></li>' for b, s in items)
    return f"""    <div class="panel{' on' if on else ''}" role="tabpanel" id="{pid}" aria-labelledby="{tid}"{'' if on else ' hidden'}>
      <div class="p-img"><img src="{IMG}{img}" alt="{alt}" loading="lazy" width="{w}" height="{h}"><span class="badge"><svg><use href="#{badge_ico}"/></svg>{badge}</span></div>
      <div class="p-body">
        <h3>{title}</h3>
        <p>{intro}</p>
        <ul class="svc-list">{lis}</ul>
        <div class="cta-row"><a class="btn btn-urgent btn-pulse" href="{TEL}"><svg class="ico phone-ico"><use href="#i-phone"/></svg>{cta}</a><a class="btn btn-outline" href="{BOOK}" target="_blank" rel="noopener">Book Online</a></div>
      </div>
    </div>
"""

treatments = f"""<!-- ============ TREATMENTS ============ -->
<section class="section tint" id="treatments">
  <div class="shell">
    <div class="head rv">
      <span class="eyebrow">Emergency Treatments</span>
      <h2>Fast Relief, <em class="acc">Done Gently</em></h2>
      <p>From an emergency root canal to an emergency tooth extraction, our Richardson team focuses on getting you out of pain first — then on saving your smile.</p>
    </div>
    <div class="tabs rv" role="tablist" aria-label="Emergency treatments">
      <button class="tab" role="tab" aria-selected="true" aria-controls="p-pain" id="t-pain"><svg><use href="#i-bolt"/></svg>Toothache &amp; Infection</button>
      <button class="tab" role="tab" aria-selected="false" aria-controls="p-broke" id="t-broke"><svg><use href="#i-tooth"/></svg>Broken Teeth</button>
      <button class="tab" role="tab" aria-selected="false" aria-controls="p-ext" id="t-ext"><svg><use href="#i-kit"/></svg>Emergency Extraction</button>
      <button class="tab" role="tab" aria-selected="false" aria-controls="p-ko" id="t-ko"><svg><use href="#i-warning"/></svg>Knocked-Out Tooth</button>
    </div>
""" + panel("p-pain", "t-pain", "emergency-dentist-richardson.jpg", "Patient with a severe toothache — emergency dentist in Richardson", 650, 475,
            "i-clock", "Same-day when possible", "Severe Toothache &amp; Abscess",
            "Throbbing pain, swelling or a pimple-like bump on the gum usually means infection. Prompt care stops it from spreading and can save the tooth.",
            [("Emergency Exam &amp; X-Rays", "Find the cause fast"), ("Emergency Root Canal", "Remove infection, keep the tooth"),
             ("Abscess Treatment", "Drain &amp; relieve swelling"), ("Gum Infection Care", "Board-certified periodontist")],
            "Call for Pain Relief", on=True) \
  + panel("p-broke", "t-broke", "dental-equipment.jpg", "Same-day CEREC crown technology at Gentle Touch Dentistry", 867, 648,
          "i-bolt", "Same-day CEREC crowns", "Chipped, Cracked or Broken Teeth",
          "A broken tooth can be sharp, sensitive and painful. We repair it quickly — often with a same-day CEREC crown, so you don't wait weeks for a lab.",
          [("Dental Bonding", "Fast repair for chips"), ("Same-Day CEREC Crowns", "Crowns in a single visit"),
           ("Lost Crown or Filling", "Re-cement or replace"), ("Temporary Repairs", "Protect the tooth now")],
          "Call to Fix It Today") \
  + panel("p-ext", "t-ext", "img-meet-our-doctors-dr-kolli.webp", "Dr. Usha Kolli, surgical-focused dentist for emergency tooth extraction", 608, 684,
          "i-grad", "Surgical-focused dentist", "Emergency Tooth Extraction",
          "Need an emergency dental extraction near you? When a tooth can't be saved, we remove it gently and comfortably — and talk you through replacement options before you leave.",
          [("Emergency Tooth Removal", "Gentle, numbed extractions"), ("Wisdom Tooth Extraction", "With Dr. Kolli"),
           ("Sedation Options", "Nitrous &amp; oral sedation"), ("Tooth Replacement", "Implants, bridges &amp; dentures")],
          "Call About an Extraction") \
  + panel("p-ko", "t-ko", "richardson-dentistry.jpg", "Gentle Touch Dentistry emergency dental office in Richardson", 867, 648,
          "i-warning", "Best within 30–60 min", "Knocked-Out or Loose Tooth",
          "Time matters. Keep the tooth moist in milk or back in its socket and call us right away — the faster you're seen, the better the chance of saving it.",
          [("Tooth Re-Implantation", "Save a knocked-out tooth"), ("Splinting Loose Teeth", "Stabilize after injury"),
           ("Soft Tissue Injuries", "Lips, gums &amp; tongue"), ("Follow-Up Care", "Root canal or crown if needed")],
          "Call Right Now") + """  </div>
</section>"""

# ----------------------------------------------------------------- first aid
AID = [
    ("Knocked-out tooth", "Pick the tooth up by the crown, not the root. Rinse gently — don't scrub. Place it back in the socket or keep it moist in milk, then call us.", "Within 30–60 min"),
    ("Chipped, cracked or loose tooth", "Rinse with warm water and save any broken pieces. Use a cold compress on your face. Hold a loose tooth gently in place and don't chew on it.", ""),
    ("Toothache or abscess", "Rinse with warm salt water and gently floss out trapped food. A cold compress and an over-the-counter pain reliever may help. Never put aspirin on your gums.", "Swelling? Call now"),
    ("Lost filling or crown", "Keep the crown safe and bring it with you. Avoid chewing on that side. Temporary dental cement from a pharmacy can protect the tooth.", ""),
    ("Broken braces wire or bracket", "Gently push a poking wire with a pencil eraser, or cover it with orthodontic wax or a cotton ball. Don't cut the wire yourself.", ""),
    ("Object stuck or soft tissue injury", "Use floss — never a sharp tool. For cuts to lips, cheeks or tongue, rinse and apply gentle pressure with clean gauze.", "Won't stop bleeding? ER"),
]
first_aid = f"""<!-- ============ FIRST AID ============ -->
<section class="section" id="first-aid">
  <div class="shell">
    <div class="head rv">
      <span class="eyebrow">First Aid</span>
      <h2>What to Do <em class="acc">Right Now</em></h2>
      <p>These steps help protect your tooth and ease the pain until you reach our emergency dentist. Call us for advice specific to your situation.</p>
    </div>
    <div data-carousel><div class="aid mswipe track-m">
""" + "".join(
    f"""      <div class="aid-card rv" data-d="{i % 3}"><span class="n">{i + 1:02d}</span><h3>{t}</h3><p>{d}</p>{f'<span class="tip">{tip}</span>' if tip else ''}</div>\n"""
    for i, (t, d, tip) in enumerate(AID)) + f"""    </div>
    <div class="dots mdots" aria-hidden="true"></div></div>
    <div class="sec-cta rv">
      <div class="cta-row center">
        <a class="btn btn-urgent btn-xl btn-pulse" href="{TEL}"><svg class="ico phone-ico"><use href="#i-phone"/></svg>Call Our Emergency Dentist</a>
        <a class="btn btn-primary btn-xl btn-shine" href="{BOOK}" target="_blank" rel="noopener"><svg class="ico"><use href="#i-cal"/></svg>Book My Slot For Today</a>
      </div>
    </div>
  </div>
</section>"""

# ------------------------------------------------------------------ why us
WHY = [
    ("i-bolt", "Same-Day Appointments", "We make room for dental emergencies the same day whenever possible — call first and we'll reserve the soonest opening."),
    ("i-heart", "Pain Relief Comes First", "We numb the area and offer nitrous oxide or oral sedation, so you're comfortable before anything else happens."),
    ("i-screen", "Fast, Accurate Diagnosis", "Low-radiation digital X-rays and intraoral photos shown on a 40-inch screen — you see exactly what we see."),
    ("i-tooth", "Same-Day CEREC Crowns", "Broken tooth? We can often design, mill and place a permanent crown in a single visit."),
    ("i-grad", "The Right Specialist In-House", "A surgical-focused dentist for extractions and a board-certified periodontist for gum infections."),
    ("i-card", "Insured or Not", "In-network with 29+ PPO plans, plus a membership plan and upfront pricing for patients without insurance."),
]
why = f"""<!-- ============ WHY US ============ -->
<section class="section dark" id="why">
  <div class="shell">
    <div class="head rv">
      <span class="eyebrow">Why Choose Us</span>
      <h2>Your Nearby Emergency Dentist, <em class="acc">Who Cares</em></h2>
      <p>A dental emergency is stressful. Our Richardson team keeps you calm, gets you out of pain and explains every option before treatment.</p>
    </div>
    <div data-carousel><div class="why mswipe track-m">
""" + "".join(
    f"""      <div class="why-card rv" data-d="{i % 3}" data-tilt><span class="num">{i + 1:02d}</span><span class="w-ico"><svg><use href="#{ico}"/></svg></span><h3>{t}</h3><p>{d}</p></div>\n"""
    for i, (ico, t, d) in enumerate(WHY)) + f"""    </div>
    <div class="dots mdots" aria-hidden="true"></div></div>
    <div class="sec-cta rv">
      <div class="cta-row center">
        <a class="btn btn-primary btn-xl btn-shine" href="{TEL}"><svg class="ico phone-ico"><use href="#i-phone"/></svg>Call {PHONE}</a>
        <a class="btn btn-ghost btn-xl" href="{BOOK}" target="_blank" rel="noopener"><svg class="ico"><use href="#i-cal"/></svg>Book Online</a>
      </div>
    </div>
  </div>
</section>"""

# --------------------------------------------------------------- visit steps
STEPS = [
    ("Call Us First", "Tell us what happened. We'll give first-aid advice and the soonest available time."),
    ("Quick Evaluation", "We examine the area and take digital X-rays to understand the problem."),
    ("Pain Relief", "We numb the area and offer nitrous oxide if needed — your comfort comes first."),
    ("Treat or Stabilize", "We fix the problem or stabilize the tooth, explaining options and costs upfront."),
    ("Follow-Up Plan", "If you need more care, like a crown or root canal, we schedule it and review your benefits."),
]
steps = f"""<!-- ============ EMERGENCY VISIT ============ -->
<section class="section ivory" id="visit-steps">
  <div class="shell">
    <div class="head rv">
      <span class="eyebrow">Your Emergency Visit</span>
      <h2>From Pain to Relief in <em class="acc">5 Simple Steps</em></h2>
      <p>Here's exactly what happens when you come to our emergency dental office in Richardson.</p>
    </div>
    <div class="steps five">
""" + "".join(f'      <div class="step rv" data-d="{i}"><h3>{t}</h3><p>{d}</p></div>\n' for i, (t, d) in enumerate(STEPS)) + f"""    </div>
    <div class="sec-cta rv"><div class="cta-row center"><a class="btn btn-urgent btn-xl btn-pulse" href="{TEL}"><svg class="ico phone-ico"><use href="#i-phone"/></svg>Start With Step 1 — Call Now</a></div>
    <p class="cta-note"><svg class="ico"><use href="#i-check"/></svg>New &amp; existing patients welcome</p></div>
  </div>
</section>"""

# --------------------------------------------------------------------- FAQ
faq = f"""<!-- ============ FAQ ============ -->
<section class="section tint" id="faq">
  <div class="shell">
    <div class="head rv">
      <span class="eyebrow">Emergency FAQ</span>
      <h2>Dental Emergency <em class="acc">Questions</em></h2>
      <p>Quick answers about emergency dental care in Richardson — or just call and ask us.</p>
    </div>
    <div class="faq">
""" + "".join(
    f'      <details class="rv"{" open" if i == 0 else ""}><summary>{q}<span class="pm" aria-hidden="true"></span></summary><div class="ans">{html_a}</div></details>\n'
    for i, (q, _, html_a) in enumerate(FAQ)) + f"""    </div>
    <div class="sec-cta rv">
      <p style="font-weight:700;margin-bottom:14px">In pain right now? Don't wait.</p>
      <div class="cta-row center">
        <a class="btn btn-urgent btn-xl btn-pulse" href="{TEL}"><svg class="ico phone-ico"><use href="#i-phone"/></svg>Call {PHONE}</a>
        <a class="btn btn-primary btn-xl btn-shine" href="{BOOK}" target="_blank" rel="noopener"><svg class="ico"><use href="#i-cal"/></svg>Book Online</a>
      </div>
    </div>
  </div>
</section>"""

# ------------------------------------------------------- shared, re-worded
creds = section("CREDENTIALS / RECOGNITION")
creds = sub(creds, '<section class="section ivory" id="credentials">', '<section class="section" id="credentials">')

doctors = section("DOCTORS")
doctors = sub(doctors, "<h2>Meet Your <em class=\"acc\">Richardson</em> Dentists</h2>", "<h2>The Emergency Dentists <em class=\"acc\">Who'll Care for You</em></h2>")
doctors = sub(doctors, "<p>Exceptional, comprehensive care — and a friendly team that makes you feel like family.</p>",
              "<p>Calm, experienced hands when you need them most — including a surgical-focused dentist and a board-certified periodontist.</p>")

reviews = section("REVIEWS")
reviews = sub(reviews, f'<a class="btn btn-primary btn-xl btn-shine" href="{BOOK}" target="_blank" rel="noopener"><svg class="ico"><use href="#i-cal"/></svg>Join Our Happy Patients</a>\n        <a class="btn btn-call btn-xl btn-pulse" href="{TEL}"><svg class="ico phone-ico"><use href="#i-phone"/></svg>{PHONE}</a>',
              f'<a class="btn btn-urgent btn-xl btn-pulse" href="{TEL}"><svg class="ico phone-ico"><use href="#i-phone"/></svg>Call {PHONE}</a>\n        <a class="btn btn-primary btn-xl btn-shine" href="{BOOK}" target="_blank" rel="noopener"><svg class="ico"><use href="#i-cal"/></svg>Book My Slot For Today</a>')
reviews = sub(reviews, "<p>Don't take our word for it — hear from the Richardson families who trust us with their smiles.</p>",
              "<p>Nervous, in pain, or worried about cost? Hear from patients who felt cared for from the first phone call.</p>")

insurance = section("INSURANCE")
insurance = sub(insurance, "<h2>In-Network With <em class=\"acc\">29+ PPO Plans</em></h2>", "<h2>Emergency Care With <em class=\"acc\">29+ PPO Plans</em></h2>")
insurance = sub(insurance, '<p>Searching "Delta Dental find a dentist" or for dentists near me that accept Cigna or MetLife? You\'ve found one. We verify your coverage and file every claim for you.</p>',
                "<p>Many plans cover emergency exams, X-rays and part of your treatment. We verify your coverage on the spot and file the claim for you — and if you don't have insurance, we'll still see you.</p>")

gallery = section("OFFICE GALLERY")
gallery = sub(gallery, '<section class="section tint" id="office">', '<section class="section" id="office">')
gallery = sub(gallery, "<h2>Step Inside Our <em class=\"acc\">Calm, Modern</em> Office</h2>", "<h2>A Calm Place to <em class=\"acc\">Get Relief</em></h2>")
gallery = sub(gallery, f'<a class="btn btn-primary btn-xl btn-shine" href="{BOOK}" target="_blank" rel="noopener"><svg class="ico"><use href="#i-cal"/></svg>Visit Us — Book Online</a>',
              f'<a class="btn btn-urgent btn-xl btn-pulse" href="{TEL}"><svg class="ico phone-ico"><use href="#i-phone"/></svg>Call {PHONE}</a>')

contact_m = section("LOCATION / CONTACT")
contact_m = sub(contact_m, "<span class=\"eyebrow\">Find Us</span>", "<span class=\"eyebrow\">Emergency Dentist Near You</span>")
contact_m = sub(contact_m, "<h2>Your Local Dentist Near <em class=\"acc\">Richardson, TX</em></h2>", "<h2>Emergency Dental Care Near <em class=\"acc\">Richardson, TX</em></h2>")
contact_m = sub(contact_m, f'<a class="btn btn-primary btn-shine" style="flex:1 1 auto" href="{BOOK}" target="_blank" rel="noopener"><svg class="ico"><use href="#i-cal"/></svg>Book Appointment</a>\n          <a class="btn btn-call btn-pulse" style="flex:1 1 auto" href="{TEL}"><svg class="ico phone-ico"><use href="#i-phone"/></svg>Call Now</a>',
                f'<a class="btn btn-urgent btn-pulse" style="flex:1 1 auto" href="{TEL}"><svg class="ico phone-ico"><use href="#i-phone"/></svg>Call Now</a>\n          <a class="btn btn-primary btn-shine" style="flex:1 1 auto" href="{BOOK}" target="_blank" rel="noopener"><svg class="ico"><use href="#i-cal"/></svg>Book Online</a>')

contact_d = section("VISIT / CONTACT (desktop)")
contact_d = sub(contact_d, '<span class="cx-eyebrow">Have a question?</span>', '<span class="cx-eyebrow">Dental emergency?</span>')
contact_d = sub(contact_d, "Call us with any question or book your visit online in a few clicks. New patients and same-day emergencies are always welcome at our Richardson dental office.",
                "Call our emergency dentist in Richardson now — we'll triage your symptoms over the phone and reserve the soonest opening. Same-day emergency appointments whenever possible.")
contact_d = sub(contact_d, f'<a class="btn btn-primary btn-xl btn-shine" href="{BOOK}" target="_blank" rel="noopener"><svg class="ico"><use href="#i-cal"/></svg>Book Online Now<svg class="ico"><use href="#i-right"/></svg></a>\n          <a class="btn btn-ghost btn-xl btn-pulse" href="{TEL}"><svg class="ico phone-ico"><use href="#i-phone"/></svg>{PHONE}</a>',
                f'<a class="btn btn-primary btn-xl btn-shine" href="{TEL}"><svg class="ico phone-ico"><use href="#i-phone"/></svg>Call {PHONE}</a>\n          <a class="btn btn-ghost btn-xl" href="{BOOK}" target="_blank" rel="noopener"><svg class="ico"><use href="#i-cal"/></svg>Book Online<svg class="ico"><use href="#i-right"/></svg></a>')

final = f"""<!-- ============ FINAL CTA ============ -->
<section class="final">
  <div class="shell">
    <span class="eyebrow rv" style="color:var(--sky)">Don't Let It Get Worse</span>
    <h2 class="rv" data-d="1">Dental Emergency? Get Relief <em class="acc">Today</em></h2>
    <p class="rv" data-d="2">Prompt dental emergency care relieves pain, stops infection from spreading and gives you the best chance of saving your tooth. Call now — we'll make room for you whenever possible.</p>
    <div class="cta-row center rv" data-d="3">
      <a class="btn btn-primary btn-xl btn-pulse btn-shine" href="{TEL}"><svg class="ico phone-ico"><use href="#i-phone"/></svg>Call {PHONE}</a>
      <a class="btn btn-ghost btn-xl" href="{BOOK}" target="_blank" rel="noopener"><svg class="ico"><use href="#i-cal"/></svg>Book My Slot For Today</a>
    </div>
  </div>
</section>"""

footer = between(SRC, '<footer class="footer">', "</footer>") + "</footer>"

mbar = f"""<!-- Mobile sticky CTA -->
<nav class="mbar" aria-label="Quick contact">
  <div class="rate"><span class="dot-urgent" aria-hidden="true"></span><span data-live-text>Same-day emergencies</span></div>
  <a class="btn btn-urgent btn-pulse" href="{TEL}"><svg class="ico phone-ico"><use href="#i-phone"/></svg>Call Now</a>
  <a class="btn btn-primary btn-shine" href="{BOOK}" target="_blank" rel="noopener"><svg class="ico"><use href="#i-cal"/></svg>Book Online</a>
</nav>

<div class="lightbox" role="dialog" aria-modal="true" aria-label="Office photo"><button type="button" aria-label="Close">&times;</button><img alt=""></div>"""

page = "\n\n".join([
    head + practice_schema + "\n" + faq_schema + "\n\n<style>" + style + "</style>\n</head>\n<body>\n",
    "<!-- Icon sprite -->" + sprite.rstrip(),
    '<div class="progress" aria-hidden="true"></div>',
    topbar, header, "<main>",
    hero, stats, conditions, offers, treatments, first_aid, why, creds, doctors,
    reviews, steps, insurance, gallery, faq, contact_m, contact_d, final,
    "</main>", footer, mbar, script, "</body>\n</html>\n",
])
OUT.write_text(page, encoding="utf-8")
print(f"wrote {OUT.name} ({len(page):,} bytes)")
