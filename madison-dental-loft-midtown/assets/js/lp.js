/* ==========================================================================
   Madison Dental Loft — Midtown Manhattan — "Use It or Lose It"
   - Google Ads / GA4 conversion event hooks
   - Live countdown to the Dec 31 benefits deadline (Eastern time)
   - Scroll-reveal (fails open), sticky header, open/closed hours logic
   ========================================================================== */
(function () {
  'use strict';

  var CONFIG = {
    PHONE_E164: '+16469309679',
    ADS_CONVERSION_ID: '',   // e.g. 'AW-123456789'
    LABEL_CALL: '',
    LABEL_BOOK: '',
    TIMEZONE: 'America/New_York',
    DEADLINE_ISO: '2026-12-31T23:59:59-05:00'   // New York is on EST (UTC-5) by Dec 31
  };

  function track(eventName, label) {
    try {
      if (typeof window.gtag === 'function') {
        window.gtag('event', eventName, { event_category: 'landing_page', event_label: document.body.getAttribute('data-lp') || 'lp' });
        if (CONFIG.ADS_CONVERSION_ID && label) window.gtag('event', 'conversion', { send_to: CONFIG.ADS_CONVERSION_ID + '/' + label });
      }
      if (typeof window.fbq === 'function') window.fbq('trackCustom', eventName);
      window.dataLayer = window.dataLayer || [];
      window.dataLayer.push({ event: eventName });
    } catch (e) { /* tracking must never break the page */ }
  }

  document.addEventListener('click', function (e) {
    var link = e.target.closest && e.target.closest('a');
    if (!link) return;
    var href = link.getAttribute('href') || '';
    if (href.indexOf('tel:') === 0) track('click_to_call', CONFIG.LABEL_CALL);
    else if (href.indexOf('allinone.dental') > -1) track('click_book_online', CONFIG.LABEL_BOOK);
    else if (href.indexOf('maps') > -1 || href.indexOf('goo.gl') > -1) track('click_directions', '');
  });

  function initCountdown() {
    var els = document.querySelectorAll('[data-countdown]');
    if (!els.length) return;
    var deadline = new Date(CONFIG.DEADLINE_ISO).getTime();
    function paint() {
      var diff = Math.max(0, deadline - Date.now());
      var d = Math.floor(diff / 86400000), h = Math.floor((diff % 86400000) / 3600000),
          m = Math.floor((diff % 3600000) / 60000), s = Math.floor((diff % 60000) / 1000);
      els.forEach(function (root) { set(root, 'd', d); set(root, 'h', h); set(root, 'm', m); set(root, 's', s); });
      if (diff <= 0) clearInterval(timer);
    }
    function set(root, key, val) { var el = root.querySelector('[data-cd-' + key + ']'); if (el) el.textContent = String(val).padStart(2, '0'); }
    paint();
    var timer = setInterval(paint, 1000);
  }

  // Mon 1 … Sun 0. [openMinutes, closeMinutes], 'select' (open only some Saturdays), or null when closed.
  var HOURS = {
    1: [540, 1080], // Mon  9:00a–6:00p
    2: [540, 1080], // Tue  9:00a–6:00p
    3: [540, 1080], // Wed  9:00a–6:00p
    4: [540, 1080], // Thu  9:00a–6:00p
    5: [540, 1020], // Fri  9:00a–5:00p
    6: 'select',    // Sat  9:00a–3:00p on select Saturdays only
    0: null         // Sun closed
  };
  // From the practice's booking calendar (Oct 2026). Confirm with the office and update as needed.
  var OPEN_SATURDAYS = ['2026-10-17', '2026-10-31', '2026-11-14', '2026-12-05', '2026-12-12'];
  var CLOSED_DATES = ['2026-11-26', '2026-11-27', '2026-12-24', '2026-12-25', '2026-12-31', '2027-01-01'];

  function localNow() {
    var parts = new Intl.DateTimeFormat('en-US', { timeZone: CONFIG.TIMEZONE, weekday: 'short', year: 'numeric', month: '2-digit', day: '2-digit', hour: 'numeric', minute: 'numeric', hour12: false }).formatToParts(new Date());
    var map = {}; parts.forEach(function (p) { map[p.type] = p.value; });
    var days = { Sun: 0, Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6 };
    return { day: days[map.weekday], ymd: map.year + '-' + map.month + '-' + map.day, minutes: (parseInt(map.hour, 10) % 24) * 60 + parseInt(map.minute, 10) };
  }

  function initHours() {
    var now; try { now = localNow(); } catch (e) { return; }
    var todayRow = document.querySelector('.hours-table tr[data-day="' + now.day + '"]');
    if (todayRow) todayRow.classList.add('is-today');
    var span = HOURS[now.day];
    var state;
    if (CLOSED_DATES.indexOf(now.ymd) > -1) state = 'closed';
    else if (span === 'select') state = (OPEN_SATURDAYS.indexOf(now.ymd) > -1 && now.minutes >= 540 && now.minutes < 900) ? 'select' : 'closed';
    else state = (span && now.minutes >= span[0] && now.minutes < span[1]) ? 'open' : 'closed';
    document.querySelectorAll('[data-open-status]').forEach(function (el) {
      var text = state === 'open' ? (el.getAttribute('data-open-text') || 'Open now')
               : state === 'select' ? (el.getAttribute('data-select-text') || 'Open select Saturdays')
               : (el.getAttribute('data-closed-text') || 'Closed right now');
      el.textContent = text;
      el.classList.toggle('is-open', state === 'open');
    });
  }

  function initStickyHeader() {
    var header = document.querySelector('.site-header');
    if (!header) return;
    var onScroll = function () { header.classList.toggle('is-stuck', window.scrollY > 8); };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  // Count numbers up from zero inside an element's first text node, e.g. "80–100%" or "$1,000–$2,000+".
  function countUp(el) {
    var node = el.firstChild;
    if (!node || node.nodeType !== 3) return;
    var original = node.nodeValue, start = null, DURATION = 1300;
    if (!/\d/.test(original)) return;
    function frame(ts) {
      if (start === null) start = ts;
      var t = Math.min(1, (ts - start) / DURATION), eased = 1 - Math.pow(1 - t, 3);
      node.nodeValue = t < 1 ? original.replace(/\d[\d,]*(\.\d+)?/g, function (num) {
        var value = parseFloat(num.replace(/,/g, '')) * eased, decimals = (num.split('.')[1] || '').length;
        var out = value.toFixed(decimals);
        return num.indexOf(',') > -1 ? Number(out).toLocaleString('en-US') : out;
      }) : original;
      if (t < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }

  function initReveal() {
    var blocks = [].slice.call(document.querySelectorAll('[data-reveal]'));
    var groups = [].slice.call(document.querySelectorAll('[data-reveal-stagger]'));
    var bands = [].slice.call(document.querySelectorAll('.final-cta'));
    var targets = blocks.concat(groups, bands);
    if (!targets.length) return;
    var reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduced || !('IntersectionObserver' in window)) return;   // content simply stays visible

    groups.forEach(function (group) {
      [].forEach.call(group.children, function (child, i) {
        if (!child.style.getPropertyValue('--reveal-delay')) child.style.setProperty('--reveal-delay', (i * 90) + 'ms');
      });
    });

    // After an element has animated in, hand it back to its own transitions (button hovers etc.).
    function settle(el) {
      var delay = parseInt(el.style.getPropertyValue('--reveal-delay'), 10) || 0;
      setTimeout(function () { el.classList.add('reveal-done'); }, delay + 900);
    }
    function show(el) {
      if (el.classList.contains('is-visible') || el.classList.contains('is-in-view')) return;
      if (el.classList.contains('final-cta')) { el.classList.add('is-in-view'); return; }
      el.classList.add('is-visible');
      if (el.hasAttribute('data-reveal-stagger')) [].forEach.call(el.children, settle);
      else settle(el);
      el.querySelectorAll('[data-count-up]').forEach(countUp);
      if (el.hasAttribute('data-count-up')) countUp(el);
    }

    document.documentElement.classList.add('reveal-ready');
    var observerAlive = false;
    var io = new IntersectionObserver(function (entries) {
      observerAlive = true;
      entries.forEach(function (entry) {
        // Reveal on entering the viewport, and anything already scrolled past (e.g. after a reload mid-page).
        if (entry.isIntersecting || entry.boundingClientRect.bottom < 0) { show(entry.target); io.unobserve(entry.target); }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -8% 0px' });
    targets.forEach(function (el) { io.observe(el); });
    // Fail open: if the observer never reports back, show everything.
    setTimeout(function () { if (!observerAlive) targets.forEach(show); }, 2500);
  }

  function boot() {
    initCountdown();
    initHours();
    initStickyHeader();
    initReveal();
    document.querySelectorAll('a[href^="#"]').forEach(function (a) {
      a.addEventListener('click', function (e) {
        var id = a.getAttribute('href');
        if (!id || id === '#') return;
        var target = document.querySelector(id);
        if (!target) return;
        e.preventDefault();
        var top = target.getBoundingClientRect().top + window.pageYOffset - 84;
        window.scrollTo({ top: top, behavior: 'smooth' });
      });
    });
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot);
  else boot();
})();
