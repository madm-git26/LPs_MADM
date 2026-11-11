
/* ============================================================================
   Town Square Dentistry — Clear Aligners LP (Boynton Beach)
   1. Google rating + verified reviews (static, from the Google Business Profile)
   2. Ad-to-page message match via ?kw= / ?utm_term=
   3. Open-now indicator in America/New_York
   4. Conversion events -> dataLayer (GTM-MJHBN9L)
   5. Gallery lightbox
   ========================================================================== */
(function () {
  'use strict';

  var BOOKING_URL   = 'https://book.allinone.dental/town-square-dentistry?referrer_id=1';
  /* ------------------------------------------------------------------------ */

  var $  = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  window.dataLayer = window.dataLayer || [];
  function track(name, params) {
    var payload = Object.assign({ event: name }, params || {});
    window.dataLayer.push(payload);
    if (typeof window.gtag === 'function') { window.gtag('event', name, params || {}); }
  }

  /* ========================== 1. STARS ==================================== */
  var STAR_FULL = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M12 2.2l2.95 5.98 6.6.96-4.77 4.65 1.13 6.57L12 17.26l-5.9 3.1 1.12-6.57L2.45 9.14l6.6-.96L12 2.2z"/></svg>';
  var STAR_HALF = '<svg viewBox="0 0 24 24" aria-hidden="true"><defs><linearGradient id="hg"><stop offset="50%" stop-color="currentColor"/><stop offset="50%" stop-color="currentColor" stop-opacity=".26"/></linearGradient></defs><path fill="url(#hg)" d="M12 2.2l2.95 5.98 6.6.96-4.77 4.65 1.13 6.57L12 17.26l-5.9 3.1 1.12-6.57L2.45 9.14l6.6-.96L12 2.2z"/></svg>';
  var STAR_EMPTY = '<svg viewBox="0 0 24 24" fill="currentColor" opacity=".26" aria-hidden="true"><path d="M12 2.2l2.95 5.98 6.6.96-4.77 4.65 1.13 6.57L12 17.26l-5.9 3.1 1.12-6.57L2.45 9.14l6.6-.96L12 2.2z"/></svg>';

  function renderStars(el, rating) {
    if (!el) return;
    var html = '';
    for (var i = 1; i <= 5; i++) {
      if (rating >= i - 0.25)      html += STAR_FULL;
      else if (rating >= i - 0.75) html += STAR_HALF;
      else                          html += STAR_EMPTY;
    }
    el.innerHTML = html;
    el.setAttribute('aria-label', rating.toFixed(1) + ' out of 5 stars');
  }

  /* ========================== 2. LIVE REVIEWS ============================= */
  /* Snapshot fallback: real reviews from the same Google feed, so the section
     never renders empty if the network call fails. Replaced by live data. */
  /* Real 5-star Google reviews of Town Square Dentistry (Google Business Profile, Nov 2026) */
  var FALLBACK = {
    rating: 4.7,
    count: 520,
    reviews: [
      { n: 'Tanya Guez-Nisenson', d: '2026-09-10', r: 5, t: 'I had a really positive experience with the staff here. Everyone was warm, welcoming, helpful, and very accommodating. I had an infection that needed attention, and they even adjusted the schedule so I could have my scaling done that day, which I really appreciated.' },
      { n: 'Roya Gandjei',        d: '2026-07-10', r: 5, t: 'I recently had my wisdom teeth removed by Dr. Indictor, and I had a really great experience. I was pretty nervous going into the procedure, but Dr. Indictor and his assistant, Jessica, were so patient and reassuring that they helped me feel calm the entire time.' },
      { n: 'R.',                  d: '2026-10-10', r: 5, t: 'Dr. Finer and her team are personable and do great work! I like the smaller office and everything runs efficiently. There has been consistent availability around my work schedule.' },
      { n: 'Kimberly Chavez',     d: '2026-11-05', r: 5, t: 'Very very professional office, everybody is so sweet, they enjoy their job you can tell. This is the best dental I have had in my whole life. Trust me when I tell you this.' },
      { n: 'Verified patient',    d: '',           r: 5, t: 'I had extreme anxiety about dental work, but Dr. Fatmi and his staff are friendly, patient and incredibly gentle. More importantly, they gave me the smile I had been missing for so many years.' }
    ]
  };

  function decodeEntities(str) {
    var t = document.createElement('textarea');
    t.innerHTML = String(str == null ? '' : str);
    return t.value;
  }

  function initials(name) {
    if (/^verified/i.test(name)) return '\u2713';
    var parts = String(name || '').trim().split(/\s+/).filter(Boolean);
    if (!parts.length) return '?';
    return (parts[0][0] + (parts.length > 1 ? parts[parts.length - 1][0] : '')).toUpperCase();
  }

  function shortName(name) {
    if (/^verified/i.test(name) || /\.$/.test(name)) return name;
    var parts = String(name || '').trim().split(/\s+/).filter(Boolean);
    if (!parts.length) return 'Google user';
    var first = parts[0].charAt(0).toUpperCase() + parts[0].slice(1).toLowerCase();
    if (parts.length === 1) return first;
    return first + ' ' + parts[parts.length - 1].charAt(0).toUpperCase() + '.';
  }

  function relDate(iso) {
    var d = new Date(iso);
    if (isNaN(d)) return '';
    return d.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
  }

  function reviewCard(rv) {
    var el = document.createElement('article');
    el.className = 'rev';

    var top = document.createElement('div');
    top.className = 'rev-top';
    var st = document.createElement('span');
    st.className = 'stars';
    renderStars(st, rv.r);
    var dt = document.createElement('span');
    dt.className = 'rev-date';
    dt.textContent = relDate(rv.d);
    top.appendChild(st); top.appendChild(dt);

    var body = document.createElement('p');
    body.className = 'rev-body';
    var txt = rv.t.length > 300 ? rv.t.slice(0, 297).trim() + '…' : rv.t;
    body.textContent = '“' + txt + '”';

    var who = document.createElement('div');
    who.className = 'rev-who';
    var av = document.createElement('span');
    av.className = 'rev-av';
    av.setAttribute('aria-hidden', 'true');
    av.textContent = initials(rv.n);
    var meta = document.createElement('div');
    var nm = document.createElement('strong'); nm.textContent = shortName(rv.n);
    var src = document.createElement('span');
    src.innerHTML = '<svg width="12" height="12" viewBox="0 0 48 48" aria-hidden="true"><path fill="#FFC107" d="M43.6 20.1H42V20H24v8h11.3C33.7 32.7 29.2 36 24 36c-6.6 0-12-5.4-12-12s5.4-12 12-12c3.1 0 5.8 1.2 7.9 3.1l5.7-5.7C34.1 6.1 29.3 4 24 4 12.9 4 4 12.9 4 24s8.9 20 20 20 20-8.9 20-20c0-1.3-.1-2.6-.4-3.9z"/><path fill="#FF3D00" d="m6.3 14.7 6.6 4.8C14.7 15.1 19 12 24 12c3.1 0 5.8 1.2 7.9 3.1l5.7-5.7C34.1 6.1 29.3 4 24 4 16.3 4 9.7 8.3 6.3 14.7z"/><path fill="#4CAF50" d="M24 44c5.2 0 9.9-2 13.4-5.2l-6.2-5.2C29.2 35.1 26.7 36 24 36c-5.2 0-9.6-3.3-11.3-7.9l-6.5 5C9.5 39.6 16.2 44 24 44z"/><path fill="#1976D2" d="M43.6 20.1H42V20H24v8h11.3c-.8 2.2-2.2 4.2-4.1 5.6l6.2 5.2C36.9 40.2 44 35 44 24c0-1.3-.1-2.6-.4-3.9z"/></svg>';
    src.appendChild(document.createTextNode(rv.n === 'Verified patient' ? ' Practice website' : ' Posted on Google'));
    meta.appendChild(nm); meta.appendChild(src);
    who.appendChild(av); who.appendChild(meta);

    el.appendChild(top); el.appendChild(body); el.appendChild(who);
    return el;
  }

  function paintReviews(data) {
    renderStars($('#heroStars'), data.rating);
    renderStars($('#scoreStars'), data.rating);
    var r1 = $('#heroRating'), r2 = $('#scoreNum');
    if (r1) r1.textContent = data.rating.toFixed(1);
    if (r2) r2.textContent = data.rating.toFixed(1);
    var c1 = $('#heroCount'), c2 = $('#scoreCount');
    if (c1) c1.textContent = data.count.toLocaleString('en-US');
    if (c2) c2.textContent = data.count.toLocaleString('en-US');

    var strip = $('#revTrack');
    if (!strip || !data.reviews.length) return;
    strip.textContent = '';
    data.reviews.forEach(function (rv) { strip.appendChild(reviewCard(rv)); });
    startMarquee(strip, $('#revRail'), 34);
  }

  /* ---- shared: clone a track once and pace translateX(-50%) by width ---- */
  function startMarquee(strip, rail, pxPerSec) {
    if (!strip || !rail) return;
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    if (strip.dataset.cloned === '1') {
      Array.prototype.slice.call(strip.querySelectorAll('[data-clone="1"]')).forEach(function (n) { n.remove(); });
    }
    var originals = Array.prototype.slice.call(strip.children);
    if (!originals.length) return;
    originals.forEach(function (n) {
      var c = n.cloneNode(true);
      c.setAttribute('aria-hidden', 'true');
      c.setAttribute('data-clone', '1');
      c.setAttribute('tabindex', '-1');
      strip.appendChild(c);
    });
    strip.dataset.cloned = '1';
    var span = strip.scrollWidth / 2;
    strip.style.animationDuration = Math.max(28, Math.round(span / pxPerSec)) + 's';
    /* only loop when the row is actually wider than its frame.
       Use a class, not an inline play-state — inline would beat the CSS
       hover/focus pause rules. */
    strip.classList.toggle('no-loop', span <= rail.clientWidth);
  }

  function loadReviews() {
    /* Static, verified reviews (no third-party feed is configured for this practice). */
    paintReviews(FALLBACK);
  }

  /* ================ 3. AD-TO-PAGE MESSAGE MATCH (Quality Score) ==========
     Append ?kw=<key> to the final URL in each ad group (or let ValueTrack
     {keyword} land in ?utm_term=) and the H1 + subhead match the search.   */
  var KW_MAP = {
    'clear-aligners':             null,
    'clear-aligners-near-me':     { h: 'Clear Aligners <em>Near You</em> in Boynton Beach' },
    'clear-aligner-dentist':      { h: 'Clear Aligner Dentist in <em>Boynton Beach</em>' },
    'invisalign':                 { h: 'Clear Aligners &amp; Invisalign<sup>&reg;</sup> in <em>Boynton Beach</em>' },
    'invisalign-near-me':         { h: 'Invisalign<sup>&reg;</sup> &amp; Clear Aligners <em>Near You</em>' },
    'invisalign-dentist':         { h: 'Your Invisalign<sup>&reg;</sup> Dentist in <em>Boynton Beach</em>' },
    'clear-aligners-for-teeth':   { h: 'Clear Aligners for Teeth in <em>Boynton Beach</em>' },
    'clear-teeth-straightening':  { h: 'Clear Teeth Straightening in <em>Boynton Beach</em>' },
    'braces-doctors-near-me':     { h: 'A Clear Alternative to Braces — <em>Near You</em> in Boynton Beach',
                                    s: 'Looking for braces doctors near you? Clear aligners straighten your teeth without metal brackets or wires — start with a free consultation, a complimentary 3D scan and free X-rays.' },
    'orthodontist-doctors-near-me': { h: 'Straighten Your Teeth <em>Near You</em> in Boynton Beach',
                                    s: 'Searching for orthodontist doctors near you? Our dentists offer clear aligners for teeth — $1500 off for a limited time, with a free consultation, 3D scan and X-rays.' },
    'orthofx':                    { h: 'OrthoFX Clear Aligners in <em>Boynton Beach</em>' },
    'teeth-straightening':        { h: 'Teeth Straightening in <em>Boynton Beach</em>' },
    'braces':                     { h: 'Clear Aligners — An Alternative to Braces in <em>Boynton Beach</em>' },
    'clear-braces':               { h: 'Clear Aligners — An Alternative to Braces in <em>Boynton Beach</em>' },
    'clear-aligners-cost':        { h: 'Clear Aligners from <em>$188/Month</em> in Boynton Beach',
                                    s: 'Limited-time offer: $1500 off clear aligners — $4499 OrthoFX clear aligners, or $188 per month. Free consultation, a complimentary 3D wellness scan and free X-rays.' },
    'invisalign-cost':            { h: 'Clear Aligners from <em>$188/Month</em> in Boynton Beach',
                                    s: 'Limited-time offer: $1500 off clear aligners — $4499 OrthoFX clear aligners, or $188 per month. Free consultation, a complimentary 3D wellness scan and free X-rays.' }
  };

  function slugify(s) {
    return String(s).toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '')
      .replace(/-in-boynton-beach(-fl)?$|-boynton-beach(-fl)?$|-fl$/g, '');
  }

  function messageMatch() {
    var qs = new URLSearchParams(window.location.search);
    var raw = qs.get('kw') || qs.get('utm_term') || '';
    if (!raw) return;
    var key = slugify(raw);
    var v = Object.prototype.hasOwnProperty.call(KW_MAP, key) ? KW_MAP[key] : null;
    if (!v) return;
    var h = $('#kwHead'), s = $('#kwSub');
    if (v.h && h) h.innerHTML = v.h;
    if (v.s && s) s.textContent = v.s;
    track('message_match', { matched_keyword: key });
  }

  /* ==================== 4. OPEN NOW (America/New_York) ==================== */
  /* Mon 08:00–19:00 · Tue–Fri 08:00–17:00 · Sat & Sun closed (hours as published on the live page) */
  function officeStatus() {
    var parts;
    try {
      parts = new Intl.DateTimeFormat('en-US', {
        timeZone: 'America/New_York', weekday: 'short', hour: 'numeric',
        minute: 'numeric', hour12: false
      }).formatToParts(new Date());
    } catch (e) { return null; }
    var get = function (t) { var p = parts.find(function (x) { return x.type === t; }); return p ? p.value : null; };
    var days = { Sun: 0, Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6 };
    var dow  = days[get('weekday')];
    var hour = parseInt(get('hour'), 10) % 24;
    var min  = parseInt(get('minute'), 10);
    if (dow == null || isNaN(hour)) return null;
    var mins = hour * 60 + min, open = null, close = null, label = '5:00 PM';
    if (dow === 1) { open = 480; close = 1140; label = '7:00 PM'; }
    else if (dow >= 2 && dow <= 5) { open = 480; close = 1020; label = '5:00 PM'; }
    if (open !== null && mins >= open && mins < close) return { open: true, text: 'Open now until ' + label };
    if (open !== null && mins < open)                  return { open: true, text: 'Opening today at 8:00 AM' };
    return { open: false, text: (dow === 5 || dow === 6 || dow === 0) ? 'Book online 24/7 — we reopen Monday at 8:00 AM' : 'Book online 24/7 — we reopen at 8:00 AM' };
  }

  function paintStatus() {
    var st = officeStatus();
    var el = $('#openNow');
    if (st && el) el.textContent = st.text;

    var today = new Date().getDay();
    $$('#hoursList li').forEach(function (li) {
      if (parseInt(li.getAttribute('data-day'), 10) === today) li.classList.add('today');
    });
  }

  /* ========================== 5. SCROLL REVEAL =========================== */
  function reveal() {
    var els = $$('.rv');
    if (!('IntersectionObserver' in window) || matchMedia('(prefers-reduced-motion: reduce)').matches) {
      els.forEach(function (e) { e.classList.add('in'); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.06 });
    els.forEach(function (e) { io.observe(e); });
  }

  /* ==================== 6. CONVERSION EVENT TRACKING ===================== */
  function wireTracking() {
    document.addEventListener('click', function (e) {
      var a = e.target.closest ? e.target.closest('[data-cta]') : null;
      if (!a) return;
      var kind = a.getAttribute('data-cta');
      var loc  = a.getAttribute('data-loc') || 'unknown';
      if (kind === 'call')            track('click_to_call',     { cta_location: loc, phone: '+15615640026' });
      else if (kind === 'book')       track('click_book_online', { cta_location: loc, booking_url: BOOKING_URL });
      else if (kind === 'directions') track('click_directions',  { cta_location: loc });
      else if (kind === 'reviews')    track('reviews_click',    { cta_location: loc });
    }, { passive: true });

    /* scroll-depth: useful as a PMax/Search engagement signal */
    var hits = {}, marks = [25, 50, 75, 90];
    window.addEventListener('scroll', function () {
      var h = document.documentElement;
      var pct = Math.round(((h.scrollTop || document.body.scrollTop) / (h.scrollHeight - h.clientHeight)) * 100);
      marks.forEach(function (m) {
        if (pct >= m && !hits[m]) { hits[m] = 1; track('scroll_depth', { percent: m }); }
      });
    }, { passive: true });
  }

  /* ==================== 7. GALLERY RAIL + LIGHTBOX ======================= */
  function wireGallery() {
    var strip = $('#galTrack'), rail = $('#galRail');
    var lb = $('#lightbox'), img = $('#lbImg'), cap = $('#lbCap');
    if (!strip || !lb) return;

    var originals = $$('.shot', strip);
    if (!originals.length) return;

    var items = originals.map(function (b) {
      var i = b.querySelector('img');
      return { src: i.getAttribute('src'), alt: i.getAttribute('alt'), cap: (b.querySelector('.shot-cap') || {}).textContent || '' };
    });

    startMarquee(strip, rail, 42);

    var idx = 0, opener = null;

    function show(n) {
      idx = (n + items.length) % items.length;
      var it = items[idx];
      img.src = it.src; img.alt = it.alt; cap.textContent = it.cap;
    }
    function open(n, from) {
      opener = from || null;
      show(n);
      lb.hidden = false;
      document.body.style.overflow = 'hidden';
      strip.classList.add('paused');
      $('#lbClose').focus();
      track('gallery_open', { image_index: idx });
    }
    function close() {
      lb.hidden = true;
      document.body.style.overflow = '';
      strip.classList.remove('paused');
      if (opener && opener.isConnected) opener.focus();
    }

    /* delegation so cloned slides work too */
    strip.addEventListener('click', function (e) {
      var b = e.target.closest ? e.target.closest('.shot') : null;
      if (!b) return;
      var n = parseInt(b.getAttribute('data-i'), 10);
      if (!isNaN(n)) open(n, b);
    });

    $('#lbClose').addEventListener('click', close);
    $('#lbPrev').addEventListener('click', function () { show(idx - 1); });
    $('#lbNext').addEventListener('click', function () { show(idx + 1); });
    lb.addEventListener('click', function (e) { if (e.target === lb) close(); });

    /* keep the rail still while a finger is on it */
    rail.addEventListener('touchstart', function () { strip.classList.add('paused'); }, { passive: true });
    rail.addEventListener('touchend', function () {
      if (lb.hidden) setTimeout(function () { strip.classList.remove('paused'); }, 2500);
    }, { passive: true });

    document.addEventListener('keydown', function (e) {
      if (lb.hidden) return;
      if (e.key === 'Escape') close();
      else if (e.key === 'ArrowLeft') show(idx - 1);
      else if (e.key === 'ArrowRight') show(idx + 1);
      else if (e.key === 'Tab') {
        var f = [$('#lbClose'), $('#lbPrev'), $('#lbNext')];
        var at = f.indexOf(document.activeElement);
        e.preventDefault();
        f[(at + (e.shiftKey ? -1 : 1) + f.length) % f.length].focus();
      }
    });

    var x0 = null;
    lb.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
    lb.addEventListener('touchend', function (e) {
      if (x0 === null) return;
      var dx = e.changedTouches[0].clientX - x0;
      if (Math.abs(dx) > 45) show(idx + (dx < 0 ? 1 : -1));
      x0 = null;
    }, { passive: true });
  }

  /* ============================== INIT ================================== */
  function init() {
    var yr = $('#yr'); if (yr) yr.textContent = new Date().getFullYear();
    renderStars($('#heroStars'), 4.7);
    renderStars($('#scoreStars'), 4.7);
    messageMatch();
    paintStatus();
    loadReviews();
    reveal();
    wireTracking();
    wireGallery();
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
