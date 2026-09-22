/* ==========================================================================
   Exceptional Dentistry of Chandler — "Use It or Lose It" landing page
   - Google Ads / GA4 conversion event hooks
   - Live countdown to the Dec 31 benefits deadline (Arizona time — no DST)
   - Scroll-reveal, animated stat counters, sticky header, open/closed hours
   ========================================================================== */
(function () {
  'use strict';

  /* ------------------------------------------------------------------
     CONFIG — paste your Google Ads conversion labels here.
     Get them from Google Ads > Goals > Conversions > (your action).
     ------------------------------------------------------------------ */
  var CONFIG = {
    PHONE_E164: '+14808062601',
    ADS_CONVERSION_ID: '',   // e.g. 'AW-123456789'
    LABEL_CALL: '',          // click-to-call conversion label
    LABEL_BOOK: '',          // book-online click conversion label
    DEADLINE_ISO: '2026-12-31T23:59:59-07:00'   // Arizona (Phoenix) does not observe DST
  };

  /* ---------------------- conversion tracking ---------------------- */
  function track(eventName, label) {
    try {
      if (typeof window.gtag === 'function') {
        window.gtag('event', eventName, {
          event_category: 'landing_page',
          event_label: document.body.getAttribute('data-lp') || 'lp'
        });
        if (CONFIG.ADS_CONVERSION_ID && label) {
          window.gtag('event', 'conversion', { send_to: CONFIG.ADS_CONVERSION_ID + '/' + label });
        }
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
    else if (href.indexOf('book.allinone.dental') > -1) track('click_book_online', CONFIG.LABEL_BOOK);
    else if (href.indexOf('maps') > -1 || href.indexOf('goo.gl') > -1) track('click_directions', '');
  });

  /* ------------------------- countdown ------------------------- */
  function initCountdown() {
    var els = document.querySelectorAll('[data-countdown]');
    if (!els.length) return;
    var deadline = new Date(CONFIG.DEADLINE_ISO).getTime();

    function paint() {
      var now = Date.now();
      var diff = Math.max(0, deadline - now);
      var d = Math.floor(diff / 86400000);
      var h = Math.floor((diff % 86400000) / 3600000);
      var m = Math.floor((diff % 3600000) / 60000);
      var s = Math.floor((diff % 60000) / 1000);
      els.forEach(function (root) {
        setField(root, 'd', d);
        setField(root, 'h', h);
        setField(root, 'm', m);
        setField(root, 's', s);
      });
      if (diff <= 0) clearInterval(timer);
    }
    function setField(root, key, val) {
      var el = root.querySelector('[data-cd-' + key + ']');
      if (el) el.textContent = String(val).padStart(2, '0');
    }
    paint();
    var timer = setInterval(paint, 1000);
  }

  /* ------------------------- hours logic -------------------------- */
  // Mon 1 … Sun 0. [openMinutes, closeMinutes] or null when closed.
  var HOURS = {
    1: [450, 960], 2: [450, 960], 3: [450, 960], 4: [450, 960], // Mon–Thu 7:30a–4:00p
    5: null, 6: null, 0: null
  };

  function phoenixNow() {
    var parts = new Intl.DateTimeFormat('en-US', {
      timeZone: 'America/Phoenix', weekday: 'short', hour: 'numeric', minute: 'numeric', hour12: false
    }).formatToParts(new Date());
    var map = {};
    parts.forEach(function (p) { map[p.type] = p.value; });
    var days = { Sun: 0, Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6 };
    return { day: days[map.weekday], minutes: parseInt(map.hour, 10) * 60 + parseInt(map.minute, 10) };
  }

  function initHours() {
    var now;
    try { now = phoenixNow(); } catch (e) { return; }
    var todayRow = document.querySelector('.hours-table tr[data-day="' + now.day + '"]');
    if (todayRow) todayRow.classList.add('is-today');
    var span = HOURS[now.day];
    var isOpen = !!span && now.minutes >= span[0] && now.minutes < span[1];
    document.querySelectorAll('[data-open-status]').forEach(function (el) {
      var openText = el.getAttribute('data-open-text') || 'Open now';
      var shutText = el.getAttribute('data-closed-text') || 'Closed right now';
      el.textContent = isOpen ? openText : shutText;
      el.classList.toggle('is-open', isOpen);
    });
  }

  /* ------------------------- sticky header ------------------------- */
  function initStickyHeader() {
    var header = document.querySelector('.site-header');
    if (!header) return;
    var onScroll = function () { header.classList.toggle('is-stuck', window.scrollY > 8); };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* ------------------------- scroll reveal -------------------------
     [data-reveal] only starts hidden once .reveal-ready lands on <html> — so
     a page that renders without executing this far (script error, ad/SEO
     crawler that never scrolls, a screenshot tool that grabs the full page
     in one shot) simply keeps every section visible instead of losing it.
     A forced-visible timer is a second safety net once JS *has* run: nobody
     ends up with permanently blank sections just because they never scrolled. */
  function initReveal() {
    var items = document.querySelectorAll('[data-reveal]');
    if (!items.length) return;
    var reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduced || !('IntersectionObserver' in window)) {
      items.forEach(function (el) { el.classList.add('is-visible'); });
      return;
    }

    document.documentElement.classList.add('reveal-ready');

    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.14, rootMargin: '0px 0px -40px 0px' });
    items.forEach(function (el) { io.observe(el); });

    setTimeout(function () {
      items.forEach(function (el) { el.classList.add('is-visible'); });
    }, 3500);
  }

  /* ------------------------- animated stat counters ------------------------- */
  function initCounters() {
    var items = document.querySelectorAll('[data-count-to]');
    if (!items.length) return;
    var reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    function animate(el) {
      var to = parseFloat(el.getAttribute('data-count-to'));
      var decimals = el.getAttribute('data-count-decimals') ? parseInt(el.getAttribute('data-count-decimals'), 10) : 0;
      var suffix = el.getAttribute('data-count-suffix') || '';
      if (reduced || isNaN(to)) { el.textContent = to.toFixed(decimals) + suffix; return; }
      var start = null, duration = 1300;
      function step(ts) {
        if (!start) start = ts;
        var progress = Math.min(1, (ts - start) / duration);
        var eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = (to * eased).toFixed(decimals) + suffix;
        if (progress < 1) requestAnimationFrame(step);
      }
      requestAnimationFrame(step);
    }

    if (!('IntersectionObserver' in window)) { items.forEach(animate); return; }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) { animate(entry.target); io.unobserve(entry.target); }
      });
    }, { threshold: 0.6 });
    items.forEach(function (el) { io.observe(el); });
  }

  /* ----------------------------- boot ----------------------------- */
  function boot() {
    initCountdown();
    initHours();
    initStickyHeader();
    initReveal();
    initCounters();

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

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
