#!/usr/bin/env python3
"""
Build the four Everything Teeth Family Dental landing pages.

    general-dentist-en.html    general-dentist-es.html
    emergency-dentist-en.html  emergency-dentist-es.html

All copy lives in the CONTENT dictionary below, so the English and Spanish
versions of a page are guaranteed to stay structurally identical — only the
strings change. Edit the strings here and re-run:

    python3 build.py

(You can also edit the generated .html files directly; just be aware a rebuild
overwrites them.)
"""

import os

HERE = os.path.dirname(os.path.abspath(__file__))

PHONE_DISPLAY = "(305) 404-6659"
PHONE_HREF = "+13054046659"
ADDRESS = "12819 SW 42nd St, Miami, FL 33175"
MAPS_URL = "https://maps.app.goo.gl/DFFwzWagf9iXXnX58"
MAP_EMBED = "https://www.google.com/maps?q=12819+SW+42nd+St,+Miami,+FL+33175&output=embed"
YEAR = 2026

# --------------------------------------------------------------------------
# Icon sprite — every icon is defined once and referenced with <use>.
# --------------------------------------------------------------------------
ICONS = {
    "star": ('0 0 576 512', 'M316.9 18C311.6 7 300.4 0 288.1 0s-23.4 7-28.8 18L195 150.3 51.4 171.5c-12 1.8-22 10.2-25.7'
             ' 21.7s-.7 24.2 7.9 32.7L137.8 329 113.2 474.7c-2 12 3 24.2 12.9 31.3s23 8 33.8 2.3l128.3-68.5 128.3'
             ' 68.5c10.8 5.7 23.9 4.9 33.8-2.3s14.9-19.3 12.9-31.3L438.5 329 542.7 225.9c8.6-8.5 11.7-21.2'
             ' 7.9-32.7s-13.7-19.9-25.7-21.7L381.2 150.3 316.9 18z'),
    "phone": ('0 0 512 512', 'M164.9 24.6c-7.7-18.6-28-28.5-47.4-23.2l-88 24C12.1 30.2 0 46 0 64C0 311.4 200.6 512 448'
              ' 512c18 0 33.8-12.1 38.6-29.5l24-88c5.3-19.4-4.6-39.7-23.2-47.4l-96-40c-16.3-6.8-35.2-2.1-46.3'
              ' 11.6L304.7 368C234.3 334.7 177.3 277.7 144 207.3L193.3 167c13.7-11.2 18.4-30 11.6-46.3l-40-96z'),
    "pin": ('0 0 384 512', 'M215.7 499.2C267 435 384 279.4 384 192C384 86 298 0 192 0S0 86 0 192c0 87.4 117 243 168.3'
            ' 307.2c12.3 15.3 35.1 15.3 47.4 0zM192 128a64 64 0 1 1 0 128 64 64 0 1 1 0-128z'),
    "clock": ('0 0 512 512', 'M256 0a256 256 0 1 1 0 512A256 256 0 1 1 256 0zM232 120l0 136c0 8 4 15.5 10.7 20l96'
              ' 64c11 7.4 25.9 4.4 33.3-6.7s4.4-25.9-6.7-33.3L280 243.2 280 120c0-13.3-10.7-24-24-24s-24 10.7-24 24z'),
    "check": ('0 0 512 512', 'M256 512A256 256 0 1 0 256 0a256 256 0 1 0 0 512zM369 209L241 337c-9.4 9.4-24.6'
              ' 9.4-33.9 0l-64-64c-9.4-9.4-9.4-24.6 0-33.9s24.6-9.4 33.9 0l47 47L335 175c9.4-9.4 24.6-9.4 33.9'
              ' 0s9.4 24.6 0 33.9z'),
    "users": ('0 0 640 512', 'M96 128a128 128 0 1 1 256 0A128 128 0 1 1 96 128zM0 482.3C0 383.8 79.8 304 178.3'
              ' 304h91.4C368.2 304 448 383.8 448 482.3c0 16.4-13.3 29.7-29.7 29.7H29.7C13.3 512 0 498.7 0'
              ' 482.3zM624 208a16 16 0 1 1 0 32H432a16 16 0 1 1 0-32h192z'),
    "card": ('0 0 576 512', 'M64 32C28.7 32 0 60.7 0 96l0 32 576 0 0-32c0-35.3-28.7-64-64-64L64 32zM576 224L0 224 0'
             ' 416c0 35.3 28.7 64 64 64l448 0c35.3 0 64-28.7 64-64l0-192zM112 352l64 0c8.8 0 16 7.2 16 16s-7.2'
             ' 16-16 16l-64 0c-8.8 0-16-7.2-16-16s7.2-16 16-16zm112 0l128 0c8.8 0 16 7.2 16 16s-7.2 16-16'
             ' 16l-128 0c-8.8 0-16-7.2-16-16s7.2-16 16-16z'),
    "globe": ('0 0 512 512', 'M352 256c0 22.2-1.2 43.6-3.3 64l-185.3 0c-2.2-20.4-3.3-41.8-3.3-64s1.2-43.6'
              ' 3.3-64l185.3 0c2.2 20.4 3.3 41.8 3.3 64zm28.8-64l123.1 0c5.3 20.5 8.1 41.9 8.1 64s-2.8 43.5-8.1'
              ' 64l-123.1 0c2.1-20.6 3.2-42 3.2-64s-1.1-43.4-3.2-64zm112.6-32l-116.7 0c-10-63.9-29.8-117.4-55.3-151.6'
              ' 78.3 20.7 142 77.5 172 151.6zm-149.1 0l-176.6 0c6.1-36.4 15.5-68.6 27-94.7 10.5-23.6 22.2-40.7'
              ' 33.5-51.5C239.4 3.2 248.7 0 256 0s16.6 3.2 27.8 13.8c11.3 10.8 23 27.9 33.5 51.5 11.6 26 21 58.2 27'
              ' 94.7zm-209 0L18.6 160C48.6 85.9 112.2 29.1 190.6 8.4C165.1 42.6 145.3 96.1 135.3 160zM8.1'
              ' 192l123.1 0c-2.1 20.6-3.2 42-3.2 64s1.1 43.4 3.2 64L8.1 320C2.8 299.5 0 278.1 0 256s2.8-43.5'
              ' 8.1-64zM194.7 446.6c-11.6-26-20.9-58.2-27-94.6l176.6 0c-6.1 36.4-15.5 68.6-27 94.6-10.5 23.6-22.2'
              ' 40.7-33.5 51.5C272.6 508.8 263.3 512 256 512s-16.6-3.2-27.8-13.8c-11.3-10.8-23-27.9-33.5-51.5zM135.3'
              ' 352c10 63.9 29.8 117.4 55.3 151.6C112.2 482.9 48.6 426.1 18.6 352l116.7 0zm358.1 0c-30 74.1-93.6'
              ' 130.9-171.9 151.6 25.5-34.2 45.2-87.7 55.3-151.6l116.7 0z'),
    "bolt": ('0 0 448 512', 'M349.4 44.6c5.6-13.7 1.6-29.5-9.8-38.9s-27.6-10-39.7-1.4l-256 176c-11.2 7.7-16 22-11.7'
             ' 34.9S50.5 236 64.1 236l86.1 0-51.6 126.4c-5.6 13.7-1.6 29.5 9.8 38.9s27.6 10 39.7 1.4l256-176c11.2-7.7'
             ' 16-22 11.7-34.9s-16.3-21.7-29.9-21.7l-86.1 0L349.4 44.6z'),
    "tooth": ('0 0 448 512', 'M186.1 52.1C169.3 39.1 148.7 32 127.5 32C74.7 32 32 74.7 32 127.5l0 6.2c0 15.8 3.7'
              ' 31.3 10.7 45.5l23.5 47.1c4.5 8.9 7.6 18.4 9.4 28.2l36.7 205.8c2 11.2 11.6 19.4 22.9 19.7s21.4-7.4'
              ' 24-18.4l28.9-121.3C192.2 323.7 207 312 224 312s31.8 11.7 35.8 28.3l28.9 121.3c2.6 11 12.7 18.7 24'
              ' 18.4s20.9-8.5 22.9-19.7l36.7-205.8c1.8-9.8 4.9-19.3 9.4-28.2l23.5-47.1c7-14.1 10.7-29.7'
              ' 10.7-45.5l0-2.1c0-55-44.6-99.6-99.6-99.6c-24.1 0-47.4 8.8-65.6 24.6l-3.2 2.8 19.5 15.2c7'
              ' 5.4 8.2 15.5 2.8 22.5s-15.5 8.2-22.5 2.8l-24.4-19-37-28.8z'),
    "shield": ('0 0 512 512', 'M256 0c4.6 0 9.2 1 13.4 2.9L457.7 82.8c22 9.3 38.4 31 38.3 57.2c-.5 99.2-41.3'
               ' 280.7-213.6 363.2c-16.7 8-36.1 8-52.8 0C57.3 420.7 16.5 239.2 16 140c-.1-26.2 16.3-47.9'
               ' 38.3-57.2L242.7 2.9C246.8 1 251.4 0 256 0z'),
    "warning": ('0 0 512 512', 'M256 32c14.2 0 27.3 7.5 34.5 19.8l216 368c7.3 12.4 7.3 27.7 .2 40.1S486.3 480 472'
                ' 480L40 480c-14.3 0-27.6-7.7-34.7-20.1s-7-27.8 .2-40.1l216-368C228.7 39.5 241.8 32 256 32zm0'
                ' 128c-13.3 0-24 10.7-24 24l0 112c0 13.3 10.7 24 24 24s24-10.7 24-24l0-112c0-13.3-10.7-24-24-24zM224'
                ' 384a32 32 0 1 1 64 0 32 32 0 1 1 -64 0z'),
    "hospital": ('0 0 640 512', 'M48 0C21.5 0 0 21.5 0 48L0 464c0 26.5 21.5 48 48 48l176 0 0-80c0-26.5 21.5-48'
                 ' 48-48s48 21.5 48 48l0 80 176 0c26.5 0 48-21.5 48-48l0-416c0-26.5-21.5-48-48-48L48 0zM272'
                 ' 88c0-8.8 7.2-16 16-16l32 0c8.8 0 16 7.2 16 16l0 40 40 0c8.8 0 16 7.2 16 16l0 32c0 8.8-7.2'
                 ' 16-16 16l-40 0 0 40c0 8.8-7.2 16-16 16l-32 0c-8.8 0-16-7.2-16-16l0-40-40 0c-8.8 0-16-7.2-16-16l0-32c0-8.8'
                 ' 7.2-16 16-16l40 0 0-40z'),
    "drop": ('0 0 384 512', 'M192 512C86 512 0 426 0 320C0 228.8 130.2 57.7 166.6 11.7C172.6 4.2 181.5 0 191.1 0l1.8'
             ' 0c9.6 0 18.5 4.2 24.5 11.7C253.8 57.7 384 228.8 384 320c0 106-86 192-192 192zM96 336c0-8.8-7.2-16-16-16'
             's-16 7.2-16 16c0 61.9 50.1 112 112 112c8.8 0 16-7.2 16-16s-7.2-16-16-16c-44.2 0-80-35.8-80-80z'),
    "kit": ('0 0 512 512', 'M184 48l144 0c4.4 0 8 3.6 8 8l0 40L176 96l0-40c0-4.4 3.6-8 8-8zm-56 8l0 40L64 96C28.7 96 0'
            ' 124.7 0 160l0 96 192 0 128 0 192 0 0-96c0-35.3-28.7-64-64-64l-64 0 0-40c0-30.9-25.1-56-56-56L184 0c-30.9'
            ' 0-56 25.1-56 56zM512 288l-192 0 0 32c0 17.7-14.3 32-32 32l-64 0c-17.7 0-32-14.3-32-32l0-32L0 288 0 416c0'
            ' 35.3 28.7 64 64 64l384 0c35.3 0 64-28.7 64-64l0-128z'),
}


def sprite() -> str:
    parts = []
    for name, (viewbox, path) in ICONS.items():
        parts.append(f'<symbol id="i-{name}" viewBox="{viewbox}"><path d="{path}"/></symbol>')
    return ('<svg xmlns="http://www.w3.org/2000/svg" style="display:none" aria-hidden="true">'
            + "".join(parts) + "</svg>")


def ico(name: str) -> str:
    return f'<svg aria-hidden="true"><use href="#i-{name}"/></svg>'


def stars(count: int = 5) -> str:
    return '<span class="stars" aria-hidden="true">' + (ico("star") * count) + "</span>"


# --------------------------------------------------------------------------
# Shared page furniture
# --------------------------------------------------------------------------
def topbar(t, page, lang) -> str:
    other = "es" if lang == "en" else "en"
    return f"""
<div class="topbar">
  <div class="shell">
    <div class="topbar-facts">
      <span>{ico('pin')}{ADDRESS}</span>
      <span class="hide-sm">{ico('clock')}{t['hours_short']}</span>
      <span class="hide-sm">{ico('check')}Se Habla Español</span>
    </div>
    <div class="lang-switch" role="group" aria-label="{t['language']}">
      <a href="{page}-en.html" hreflang="en"{' class="is-active"' if lang == 'en' else ''}>EN</a>
      <a href="{page}-es.html" hreflang="es"{' class="is-active"' if lang == 'es' else ''}>ES</a>
    </div>
  </div>
</div>"""


def header(t) -> str:
    return f"""
<header class="site-header">
  <div class="shell">
    <span class="brand">
      <img src="assets/img/img-Everything-Teeth-Family-Dentist-logo.svg" width="350" height="91"
           alt="Everything Teeth Family Dental — Miami, FL">
    </span>
    <div class="header-actions">
      <a class="header-phone" href="tel:{PHONE_HREF}">
        <small>{t['header_call_label']}</small>
        <strong>{PHONE_DISPLAY}</strong>
      </a>
      <a class="btn btn-navy" href="tel:{PHONE_HREF}">{ico('phone')}{t['call_now']}</a>
      <a class="btn btn-primary btn-book-header" href="#book">{t['header_book']}</a>
    </div>
  </div>
</header>"""


def lead_form(t, prefix: str, options) -> str:
    opts = "".join(f"<option>{o}</option>" for o in options)
    return f"""
      <div class="lead-card" id="book">
        <h2>{t['form_title']}</h2>
        <p class="lead-note">{t['form_note']}</p>

        <form data-lp-form novalidate
              data-msg-required="{t['err_required']}"
              data-msg-phone="{t['err_phone']}"
              data-msg-email="{t['err_email']}"
              data-msg-ok="{t['form_ok']}"
              data-msg-fallback="{t['form_fallback']}"
              data-msg-sending="{t['form_sending']}">

          <div class="hp-field" aria-hidden="true">
            <label>Leave this empty<input type="text" name="company" tabindex="-1" autocomplete="off"></label>
          </div>

          <div class="field">
            <label for="{prefix}-name">{t['f_name']}</label>
            <input type="text" id="{prefix}-name" name="name" required autocomplete="name" placeholder="{t['f_name_ph']}">
            <span class="err"></span>
          </div>

          <div class="field">
            <label for="{prefix}-phone">{t['f_phone']}</label>
            <input type="tel" id="{prefix}-phone" name="phone" required autocomplete="tel" placeholder="(305) 000-0000">
            <span class="err"></span>
          </div>

          <div class="field">
            <label for="{prefix}-email">{t['f_email']}</label>
            <input type="email" id="{prefix}-email" name="email" required autocomplete="email" placeholder="{t['f_email_ph']}">
            <span class="err"></span>
          </div>

          <div class="field">
            <label for="{prefix}-service">{t['f_service']}</label>
            <select id="{prefix}-service" name="service" required>
              <option value="">{t['f_service_ph']}</option>
              {opts}
            </select>
            <span class="err"></span>
          </div>

          <button class="btn btn-primary btn-block btn-lg" type="submit">{t['f_submit']}</button>
          <div class="form-status" role="status" aria-live="polite"></div>
          <p class="form-legal">{t['form_legal']} <a href="tel:{PHONE_HREF}"><strong>{PHONE_DISPLAY}</strong></a>.</p>
        </form>
      </div>"""


def trust_strip(items) -> str:
    cells = "".join(
        f'<div class="trust-item">{ico(icon)}<span><strong>{title}</strong>{sub}</span></div>'
        for icon, title, sub in items
    )
    return f'<section class="trust-strip"><div class="shell">{cells}</div></section>'


def reviews_section(t, reviews) -> str:
    cards = ""
    for name, text in reviews:
        cards += f"""
      <article class="review-card">
        {stars()}
        <blockquote>{text}</blockquote>
        <div class="who">
          <span class="avatar" aria-hidden="true">{name[0]}</span>
          <div><strong>{name}</strong><span>{t['review_source']}</span></div>
        </div>
      </article>"""

    return f"""
<section class="section section--soft" id="reviews">
  <div class="shell">
    <div class="section-head">
      <span class="kicker">{t['reviews_kicker']}</span>
      <h2>{t['reviews_title']}</h2>
    </div>

    <div class="rating-summary">
      <div class="score">5.0</div>
      <div>
        {stars()}
        <div class="meta"><strong>{t['reviews_count']}</strong>{t['reviews_meta']}</div>
      </div>
      <a class="btn btn-outline" href="{MAPS_URL}" target="_blank" rel="noopener">{t['reviews_cta']}</a>
    </div>

    <div class="review-grid">{cards}
    </div>
  </div>
</section>"""


def location_section(t, urgent: bool = False) -> str:
    days = [
        ("1", t["mon"], "10:30 am – 6:30 pm", False),
        ("2", t["tue"], t["closed"], True),
        ("3", t["wed"], "10:30 am – 6:30 pm", False),
        ("4", t["thu"], "10:30 am – 6:30 pm", False),
        ("5", t["fri"], "7:30 am – 3:30 pm", False),
        ("6", t["sat"], t["closed"], True),
        ("0", t["sun"], t["closed"], True),
    ]
    rows = ""
    for d, label, hours, shut in days:
        cls = ' class="is-closed"' if shut else ""
        rows += f'<tr data-day="{d}"{cls}><th scope="row">{label}</th><td>{hours}</td></tr>'
    note = f'<p class="plan-fine">{t["hours_note"]}</p>' if urgent else ""

    return f"""
<section class="section section--sky" id="location">
  <div class="shell">
    <div class="loc-wrap">
      <div class="loc-info">
        <h2>{t['loc_title']}</h2>

        <div class="loc-line">{ico('pin')}
          <div>
            <strong>Everything Teeth Family Dental</strong>
            <a href="{MAPS_URL}" target="_blank" rel="noopener">{ADDRESS} — {t['directions']}</a>
          </div>
        </div>

        <div class="loc-line">{ico('phone')}
          <div><strong>{t['call_or_text']}</strong><a href="tel:{PHONE_HREF}">{PHONE_DISPLAY}</a></div>
        </div>

        <div class="loc-line">{ico('clock')}
          <div>
            <strong>{t['office_hours']}</strong>
            <span data-open-status data-open-text="{t['open_now']}" data-closed-text="{t['closed_now']}">{t['office_hours']}</span>
          </div>
        </div>

        <table class="hours-table"><tbody>{rows}</tbody></table>
        {note}
        <a class="btn btn-primary btn-lg" href="{'tel:' + PHONE_HREF if urgent else '#book'}">{t['loc_cta']}</a>
      </div>

      <div class="loc-map-wrap">
        <div class="loc-map-fallback">
          {ico('pin')}
          <p><strong>{ADDRESS}</strong></p>
          <a class="btn btn-light" href="{MAPS_URL}" target="_blank" rel="noopener">{t['directions']}</a>
        </div>
        <iframe class="loc-map" src="{MAP_EMBED}"
                title="{t['map_title']}"
                loading="lazy" referrerpolicy="no-referrer-when-downgrade" allowfullscreen></iframe>
      </div>
    </div>
  </div>
</section>"""


def doctors_section(t, navy: bool = False) -> str:
    cls = " section--navy" if navy else ""
    return f"""
<section class="section{cls}" id="doctors">
  <div class="shell">
    <div class="section-head">
      <span class="script-accent">{t['docs_script']}</span>
      <h2>{t['docs_title']}</h2>
      <p>{t['docs_sub']}</p>
    </div>

    <div class="doc-grid">
      <article class="doc-card">
        <div class="photo"><img src="assets/img/img-meet-our-dentists-Dr-Omar-Morell.webp" alt="Dr. Omar Morell, DMD" loading="lazy"></div>
        <div class="body">
          <h3>Dr. Omar Morell, DMD</h3>
          <div class="role">{t['omar_role']}</div>
          <p>{t['omar_bio']}</p>
          <ul>
            <li>{t['edu_fiu']}</li>
            <li>{t['edu_lecom']}</li>
            <li>{t['omar_extra']}</li>
          </ul>
        </div>
      </article>

      <article class="doc-card">
        <div class="photo"><img src="assets/img/img-meet-our-dentists-Dr-Diana-Morell.webp" alt="Dr. Diana Morell, DMD" loading="lazy"></div>
        <div class="body">
          <h3>Dr. Diana Morell, DMD</h3>
          <div class="role">{t['diana_role']}</div>
          <p>{t['diana_bio']}</p>
          <ul>
            <li>{t['edu_fiu']}</li>
            <li>{t['edu_lecom']}</li>
            <li>{t['diana_extra']}</li>
          </ul>
        </div>
      </article>
    </div>
  </div>
</section>"""


def payment_section(t, compact: bool = False) -> str:
    """Offers + Premium Patient Program + insurance/financing, kept deliberately tight."""
    offers = ""
    for i, o in enumerate(t["offers"]):
        featured = " is-featured" if o.get("featured") else ""
        tag = f'<span class="tag">{o["tag"]}</span>' if o.get("tag") else ""
        per = f'<span class="per">{o["per"]}</span>' if o.get("per") else ""
        btn = "btn-primary" if o.get("featured") else "btn-outline"
        href = "tel:" + PHONE_HREF if o.get("call") else "#book"
        offers += f"""
      <div class="offer-card{featured}">{tag}
        <h3>{o['title']}</h3>
        <div class="amount"><sup>$</sup>{o['amount']}{per}</div>
        <p>{o['copy']}</p>
        <a class="btn {btn} btn-block" href="{href}">{o['cta']}</a>
        <p class="fine">{o['fine']}</p>
      </div>"""

    includes = "".join(f"<li>{x}</li>" for x in t["ppp_includes"])

    plan = f"""
    <div class="plan-wrap">
      <div class="plan-prices">
        <h3>{t['ppp_title']}</h3>
        <p class="lede">{t['ppp_lede']}</p>
        <div class="price-row"><span class="who">{t['ppp_adult']}</span><span class="amt">$300<span>{t['per_year']}</span></span></div>
        <div class="price-row"><span class="who">{t['ppp_child']}</span><span class="amt">$175<span>{t['per_year']}</span></span></div>
        <div class="price-row"><span class="who">{t['ppp_family']}</span><span class="amt">$200<span>{t['per_year']}</span></span></div>
        <a class="btn btn-primary btn-block btn-lg" href="#book" style="margin-top:22px;">{t['ppp_cta']}</a>
      </div>
      <div class="plan-includes">
        <h4>{t['ppp_included']}</h4>
        <ul>{includes}</ul>
        <div class="plan-discount"><strong>{t['ppp_discount_head']}</strong><br>{t['ppp_discount_body']}</div>
        <p class="plan-fine">{t['ppp_fine']}</p>
      </div>
    </div>

    <div class="pay-grid">
      <div class="pay-card">
        <img src="assets/img/img-Dental-Insurance.svg" alt="" aria-hidden="true">
        <div>
          <h3>{t['ins_title']}</h3>
          <p>{t['ins_copy']}</p>
          <div class="cov"><b>{t['cov_prev']}</b><b>{t['cov_minor']}</b><b>{t['cov_major']}</b></div>
        </div>
      </div>
      <div class="pay-card">
        <img src="assets/img/img-Financing.svg" alt="" aria-hidden="true">
        <div><h3>{t['fin_title']}</h3><p>{t['fin_copy']}</p></div>
      </div>
      <div class="pay-card">
        <img src="assets/img/img-Premium-Patient-Program.svg" alt="" aria-hidden="true">
        <div><h3>{t['inhouse_title']}</h3><p>{t['inhouse_copy']}</p></div>
      </div>
    </div>"""

    section_cls = "section section--soft" if compact else "section"
    return f"""
<section class="{section_cls}" id="offers">
  <div class="shell">
    <div class="section-head">
      <span class="kicker">{t['pay_kicker']}</span>
      <h2>{t['pay_title']}</h2>
      <p>{t['pay_sub']}</p>
    </div>

    <div class="offer-grid">{offers}
    </div>
{plan}

    <p style="text-align:center;font-size:13.5px;color:#8b9aa8;margin-top:24px;">{t['pay_disclaimer']}</p>
  </div>
</section>"""


def final_cta(t, bg: str, urgent: bool = False) -> str:
    bullets = "".join(f"<li>{b}</li>" for b in t["final_points"])
    primary = f'<a class="btn btn-primary btn-lg{" btn-pulse" if urgent else ""}" href="tel:{PHONE_HREF}">{ico("phone")}{t["call_display"]}</a>'
    secondary = f'<a class="btn btn-ghost-light btn-lg" href="#book">{t["final_secondary"]}</a>'
    return f"""
<section class="final-cta" style="background-image:url('assets/img/{bg}');">
  <div class="shell">
    <div class="final-grid">
      <div>
        <h2>{t['final_title']}</h2>
        <p>{t['final_copy']}</p>
        <div class="final-actions">{primary}{secondary}</div>
      </div>
      <div><ul class="hero-points" style="grid-template-columns:1fr;">{bullets}</ul></div>
    </div>
  </div>
</section>"""


def bottom_bar(t) -> str:
    return f"""
<div class="bottom-bar">
  <div class="shell">
    <p>&copy; {YEAR} Everything Teeth Family Dental. {t['rights']}</p>
    <p class="disclaimer">{ADDRESS} &middot; {PHONE_DISPLAY} &middot; {t['legal']}</p>
  </div>
</div>

<div class="mobile-bar">
  <a class="btn btn-navy" href="tel:{PHONE_HREF}">{ico('phone')}{t['call_now']}</a>
  <a class="btn btn-primary" href="#book">{t['mobile_book']}</a>
</div>"""


def schema(t) -> str:
    return f"""<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Dentist",
  "name": "Everything Teeth Family Dental",
  "url": "https://www.everythingteethmiami.com/",
  "telephone": "+1-305-404-6659",
  "address": {{
    "@type": "PostalAddress",
    "streetAddress": "12819 SW 42nd St",
    "addressLocality": "Miami",
    "addressRegion": "FL",
    "postalCode": "33175",
    "addressCountry": "US"
  }},
  "geo": {{ "@type": "GeoCoordinates", "latitude": 25.7302474, "longitude": -80.4021682 }},
  "aggregateRating": {{ "@type": "AggregateRating", "ratingValue": "5.0", "reviewCount": "640" }},
  "openingHoursSpecification": [
    {{ "@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday","Wednesday","Thursday"], "opens": "10:30", "closes": "18:30" }},
    {{ "@type": "OpeningHoursSpecification", "dayOfWeek": "Friday", "opens": "07:30", "closes": "15:30" }}
  ]
}}
</script>"""


def shell(lang, page, t, body_class, body_html) -> str:
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{t['title']}</title>
<meta name="description" content="{t['description']}">
<meta name="robots" content="noindex, nofollow">
<link rel="icon" href="assets/img/cropped-img-Everything-Teeth-Family-Dentist-social-favicon.png">
<link rel="alternate" hreflang="en" href="{page}-en.html">
<link rel="alternate" hreflang="es" href="{page}-es.html">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Instrument+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&family=Karla:wght@400;500;700&family=Poppins:wght@400;500;600;700&family=The+Nautigal:wght@400;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/css/theme.css">
{schema(t)}
</head>
<body data-lp="{page}-{lang}"{f' class="{body_class}"' if body_class else ''}>
{sprite()}
{body_html}
<script src="assets/js/lp.js"></script>
</body>
</html>
"""


# ==========================================================================
# PAGE TEMPLATES
# ==========================================================================
def build_general(lang, t) -> str:
    page = "general-dentist"

    groups = ""
    for g in t["service_groups"]:
        cards = "".join(
            f'<div class="svc-card"><span class="tick" aria-hidden="true"></span>'
            f'<div><h4>{n}</h4><p>{d}</p></div></div>'
            for n, d in g["items"]
        )
        groups += f"""
    <div class="svc-group">
      <div class="svc-group-head">
        <img src="assets/img/{g['icon']}" alt="" aria-hidden="true">
        <div><h3>{g['title']}</h3><p>{g['blurb']}</p></div>
      </div>
      <div class="svc-grid">{cards}</div>
    </div>"""

    why = "".join(
        f'<div class="why-card"><span class="num">{i + 1:02d}</span><h3>{h}</h3><p>{p}</p></div>'
        for i, (h, p) in enumerate(t["why"])
    )
    team = "".join(
        f'<div class="team-item"><strong>{n}</strong><span>{r}</span></div>' for n, r in t["team"]
    )
    steps = "".join(f'<div class="step"><h3>{h}</h3><p>{p}</p></div>' for h, p in t["steps"])
    points = "".join(f"<li>{p}</li>" for p in t["hero_points"])

    body = f"""
{topbar(t, page, lang)}
{header(t)}

<section class="hero" style="background-image:url('assets/img/img-Where-Comfort-Meets-Modern-Dental-Care.webp');">
  <div class="shell">
    <div class="hero-grid">
      <div class="hero-copy">
        <span class="hero-eyebrow">{t['hero_eyebrow']}</span>
        <h1>{t['hero_h1']} <span class="accent">{t['hero_h1_accent']}</span></h1>
        <p class="hero-sub">{t['hero_sub']}</p>
        <ul class="hero-points">{points}</ul>
        <div class="hero-cta">
          <a class="btn btn-primary btn-lg" href="#book">{t['hero_cta']}</a>
          <a class="btn btn-ghost-light btn-lg" href="tel:{PHONE_HREF}">{ico('phone')}{PHONE_DISPLAY}</a>
        </div>
        <div class="hero-offer">
          <div class="price">$159</div>
          <div class="copy"><strong>{t['hero_offer_title']}</strong>{t['hero_offer_copy']}</div>
        </div>
        <div class="hero-rating">{stars()}<span><strong>5.0</strong> {t['hero_rating']}</span></div>
      </div>
{lead_form(t, 'g', t['form_options'])}
    </div>
  </div>
</section>

{trust_strip(t['trust'])}

<section class="section" id="services">
  <div class="shell">
    <div class="section-head">
      <span class="kicker">{t['svc_kicker']}</span>
      <h2>{t['svc_title']}</h2>
      <p>{t['svc_sub']}</p>
    </div>
{groups}
    <div style="text-align:center;margin-top:40px;">
      <a class="btn btn-primary btn-lg" href="#book">{t['svc_cta']}</a>
      <a class="btn btn-outline btn-lg" href="tel:{PHONE_HREF}" style="margin-left:10px;">{t['call_display']}</a>
    </div>
  </div>
</section>

<section class="section section--navy">
  <div class="shell">
    <div class="section-head">
      <span class="kicker">{t['why_kicker']}</span>
      <h2>{t['why_title']}</h2>
      <p>{t['why_sub']}</p>
    </div>
    <div class="why-grid">{why}</div>
  </div>
</section>

{doctors_section(t)}

<section class="section section--sky section--tight">
  <div class="shell">
    <div class="section-head">
      <span class="kicker">{t['team_kicker']}</span>
      <h2>{t['team_title']}</h2>
      <p>{t['team_sub']}</p>
    </div>
    <div class="team-wrap">
      <div class="team-photo"><img src="assets/img/img-team.webp" alt="{t['team_photo_alt']}" loading="lazy"></div>
      <div class="team-list">{team}</div>
    </div>
  </div>
</section>

{payment_section(t)}
{reviews_section(t, t['reviews'])}

<section class="section">
  <div class="shell">
    <div class="section-head">
      <span class="kicker">{t['steps_kicker']}</span>
      <h2>{t['steps_title']}</h2>
      <p>{t['steps_sub']}</p>
    </div>
    <div class="steps">{steps}</div>
  </div>
</section>

{location_section(t)}
{final_cta(t, 'img-Patients.webp')}
{bottom_bar(t)}"""

    return shell(lang, page, t, "", body)


def build_emergency(lang, t) -> str:
    page = "emergency-dentist"

    conds = "".join(
        f'<div class="cond-card"><span class="ico">{ico(icon)}</span><h3>{h}</h3><p>{p}</p></div>'
        for icon, h, p in t["conditions"]
    )
    steps = "".join(f'<div class="step"><h3>{h}</h3><p>{p}</p></div>' for h, p in t["firstaid"])
    why = "".join(
        f'<div class="why-card"><span class="num">{i + 1:02d}</span><h3>{h}</h3><p>{p}</p></div>'
        for i, (h, p) in enumerate(t["why"])
    )
    points = "".join(f"<li>{p}</li>" for p in t["hero_points"])

    body = f"""
{topbar(t, page, lang)}
{header(t)}

<section class="hero" style="background-image:url('assets/img/img-inner-banner-Everything-Teeth-Family-Dentist.webp');">
  <div class="shell">
    <div class="hero-grid">
      <div class="hero-copy">
        <span class="hero-eyebrow">{ico('warning')}{t['hero_eyebrow']}</span>
        <h1>{t['hero_h1']} <span class="accent">{t['hero_h1_accent']}</span></h1>
        <p class="hero-sub">{t['hero_sub']}</p>
        <ul class="hero-points">{points}</ul>

        <div class="hero-cta">
          <a class="btn btn-primary btn-lg btn-pulse" href="tel:{PHONE_HREF}">{ico('phone')}{t['hero_call_cta']}</a>
          <a class="btn btn-ghost-light btn-lg" href="#book">{t['hero_cta2']}</a>
        </div>

        <p style="font-size:15px;color:rgba(255,255,255,.9);margin:-8px 0 20px;">
          <strong data-open-status data-open-text="{t['open_now']}" data-closed-text="{t['closed_now']}">&nbsp;</strong>
        </p>

        <div class="hero-offer">
          <div class="price">$75</div>
          <div class="copy"><strong>{t['hero_offer_title']}</strong>{t['hero_offer_copy']}</div>
        </div>

        <div class="hero-rating">{stars()}<span><strong>5.0</strong> {t['hero_rating']}</span></div>
      </div>
{lead_form(t, 'e', t['form_options'])}
    </div>
  </div>
</section>

{trust_strip(t['trust'])}

<section class="section" id="conditions">
  <div class="shell">
    <div class="section-head">
      <span class="kicker">{t['cond_kicker']}</span>
      <h2>{t['cond_title']}</h2>
      <p>{t['cond_sub']}</p>
    </div>
    <div class="cond-grid">{conds}</div>
    <div style="text-align:center;margin-top:38px;">
      <a class="btn btn-primary btn-lg btn-pulse" href="tel:{PHONE_HREF}">{ico('phone')}{t['call_display']}</a>
    </div>
  </div>
</section>

<section class="section section--sky">
  <div class="shell">
    <div class="section-head">
      <span class="kicker">{t['fa_kicker']}</span>
      <h2>{t['fa_title']}</h2>
      <p>{t['fa_sub']}</p>
    </div>
    <div class="steps">{steps}</div>
    <div class="warn-note">{ico('hospital')}<p>{t['fa_warning']}</p></div>
  </div>
</section>

<section class="section section--navy">
  <div class="shell">
    <div class="section-head">
      <span class="kicker">{t['why_kicker']}</span>
      <h2>{t['why_title']}</h2>
      <p>{t['why_sub']}</p>
    </div>
    <div class="why-grid">{why}</div>
    <div style="text-align:center;margin-top:38px;">
      <a class="btn btn-primary btn-lg" href="tel:{PHONE_HREF}">{ico('phone')}{t['call_display']}</a>
    </div>
  </div>
</section>

{doctors_section(t)}
{payment_section(t, compact=True)}
{reviews_section(t, t['reviews'])}
{location_section(t, urgent=True)}
{final_cta(t, 'img-Patients.webp', urgent=True)}
{bottom_bar(t)}"""

    return shell(lang, page, t, "is-emergency", body)


# ==========================================================================
# CONTENT
# ==========================================================================
from content import CONTENT  # noqa: E402


def main():
    pages = {
        ("general-dentist", "en"): build_general,
        ("general-dentist", "es"): build_general,
        ("emergency-dentist", "en"): build_emergency,
        ("emergency-dentist", "es"): build_emergency,
    }
    for (page, lang), builder in pages.items():
        html = builder(lang, CONTENT[page][lang])
        path = os.path.join(HERE, f"{page}-{lang}.html")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(html)
        print(f"built {os.path.basename(path)}  ({len(html):,} bytes)")


if __name__ == "__main__":
    main()
