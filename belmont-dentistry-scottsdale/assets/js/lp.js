/* Belmont Dentistry Scottsdale — landing page behaviour.
   Plain JS, no dependencies. Everything degrades gracefully: with JS off the
   page is fully readable and every call / book link still works. */
(function () {
  'use strict';

  var doc = document.documentElement;
  doc.classList.add('js');

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  var isPhone = function () { return window.matchMedia('(max-width: 760px)').matches; };

  /* ------------------------------------------------------------------
     Conversion tracking — fires to dataLayer (GTM), gtag and fbq if present.
     Fill in the Google Ads IDs once the account's conversion actions exist.
     ------------------------------------------------------------------ */
  var TRACKING = {
    ADS_CONVERSION_ID: '',   // e.g. 'AW-123456789'
    LABEL_CALL: '',          // click-to-call conversion label
    LABEL_BOOK: ''           // book-online click conversion label
  };
  window.dataLayer = window.dataLayer || [];

  function track(eventName, label, detail) {
    window.dataLayer.push({ event: eventName, lp_page: document.body.dataset.page || '', lp_location: detail || '' });
    if (typeof window.gtag === 'function') {
      window.gtag('event', eventName, { event_category: 'landing_page', event_label: detail || '' });
      if (TRACKING.ADS_CONVERSION_ID && label) {
        window.gtag('event', 'conversion', { send_to: TRACKING.ADS_CONVERSION_ID + '/' + label });
      }
    }
    if (typeof window.fbq === 'function') {
      window.fbq('track', eventName === 'click_book_online' ? 'Schedule' : 'Contact');
    }
  }

  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href]');
    if (!a) return;
    var href = a.getAttribute('href') || '';
    var where = a.dataset.cta || (a.closest('[id]') ? a.closest('[id]').id : '');
    if (href.indexOf('tel:') === 0) track('click_to_call', TRACKING.LABEL_CALL, where);
    else if (href.indexOf('book.allinone.dental') > -1) track('click_book_online', TRACKING.LABEL_BOOK, where);
    else if (href.indexOf('maps.app.goo.gl') > -1 || href.indexOf('google.com/maps') > -1) track('click_directions', '', where);
  });

  /* ------------------------------------------------------------------
     Header shadow on scroll
     ------------------------------------------------------------------ */
  var header = document.querySelector('.site-header');
  function onScroll() {
    if (header) header.classList.toggle('scrolled', window.scrollY > 10);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ------------------------------------------------------------------
     Background videos: only download & play once on screen, respect
     reduced motion, never override a manual pause.
     ------------------------------------------------------------------ */
  function setupVideo(video) {
    var toggle = video.closest('section, .split-media') && video.closest('section, .split-media').querySelector('.video-toggle');
    var userPaused = false;
    var loaded = false;

    function load() {
      if (loaded) return;
      loaded = true;
      video.querySelectorAll('source[data-src]').forEach(function (s) { s.src = s.dataset.src; });
      video.load();
    }
    function play() {
      if (userPaused || reduceMotion) return;
      load();
      var p = video.play();
      if (p && p.catch) p.catch(function () { if (toggle) toggle.classList.add('paused'); });
    }
    video.addEventListener('playing', function () {
      video.classList.add('playing');
      if (toggle) toggle.classList.remove('paused');
    });
    video.addEventListener('pause', function () { if (toggle) toggle.classList.add('paused'); });

    if (toggle) {
      toggle.addEventListener('click', function () {
        if (video.paused) { userPaused = false; reduceMotion = false; play(); }
        else { userPaused = true; video.pause(); }
      });
    }
    if (reduceMotion && toggle) toggle.classList.add('paused');

    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting) play();
          else if (!video.paused) video.pause();
        });
      }, { threshold: 0.15 }).observe(video);
    } else {
      play();
    }
  }
  // Defer video work until the page itself has loaded so it never competes
  // with the headline, CTAs and images for bandwidth.
  function initVideos() { document.querySelectorAll('video[data-lazy]').forEach(setupVideo); }
  if (document.readyState === 'complete') initVideos();
  else window.addEventListener('load', initVideos);

  /* ------------------------------------------------------------------
     Reveal on scroll
     ------------------------------------------------------------------ */
  var revealEls = document.querySelectorAll('[data-reveal]');
  if ('IntersectionObserver' in window && !reduceMotion) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    revealEls.forEach(function (el) { io.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add('in'); });
  }

  /* ------------------------------------------------------------------
     3D tilt — desktop with a real mouse only
     ------------------------------------------------------------------ */
  if (finePointer && !reduceMotion) {
    document.querySelectorAll('.tilt').forEach(function (el) {
      var max = parseFloat(el.dataset.tilt || '8');
      var glare = document.createElement('span');
      glare.className = 'tilt-glare';
      el.appendChild(glare);
      var raf = null;
      el.addEventListener('mousemove', function (e) {
        var r = el.getBoundingClientRect();
        var x = (e.clientX - r.left) / r.width;
        var y = (e.clientY - r.top) / r.height;
        if (raf) cancelAnimationFrame(raf);
        raf = requestAnimationFrame(function () {
          el.style.transition = 'transform .12s ease-out, box-shadow .4s';
          el.style.transform = 'perspective(1000px) rotateX(' + ((0.5 - y) * max).toFixed(2) + 'deg) rotateY(' + ((x - 0.5) * max).toFixed(2) + 'deg) translateY(-6px)';
          el.style.setProperty('--gx', (x * 100).toFixed(1) + '%');
          el.style.setProperty('--gy', (y * 100).toFixed(1) + '%');
        });
      });
      el.addEventListener('mouseleave', function () {
        if (raf) cancelAnimationFrame(raf);
        el.style.transition = 'transform .6s cubic-bezier(.2,.8,.2,1), box-shadow .4s';
        el.style.transform = '';
      });
    });

    // gentle parallax on the hero card & watermark
    var heroCard = document.querySelector('.hero-card');
    var hero = document.querySelector('.hero');
    if (hero && heroCard) {
      hero.addEventListener('mousemove', function (e) {
        var r = hero.getBoundingClientRect();
        var x = (e.clientX - r.left) / r.width - 0.5;
        var y = (e.clientY - r.top) / r.height - 0.5;
        heroCard.style.transform = 'perspective(1200px) rotateY(' + (x * -7).toFixed(2) + 'deg) rotateX(' + (y * 6).toFixed(2) + 'deg)';
      });
      hero.addEventListener('mouseleave', function () { heroCard.style.transform = ''; });
    }
  }

  /* ------------------------------------------------------------------
     Carousels: arrows, dots, auto-advance (phones only, stops on touch)
     ------------------------------------------------------------------ */
  document.querySelectorAll('[data-carousel]').forEach(function (car) {
    var track = car.querySelector('.carousel-track');
    // only visible children count as slides (e.g. the Why Belmont photo is hidden on phones)
    function visible() { return Array.prototype.filter.call(track.children, function (el) { return el.offsetWidth > 0; }); }
    var dotsWrap = car.querySelector('.dots');
    var prev = car.querySelector('[data-prev]');
    var next = car.querySelector('[data-next]');
    var auto = car.hasAttribute('data-auto');
    var mobileOnly = car.classList.contains('m-carousel');
    var timer = null;
    var touched = false;

    function active() { return !mobileOnly || isPhone(); }
    function perView() {
      var first = visible()[0];
      if (!first) return 1;
      return Math.max(1, Math.round(track.clientWidth / first.getBoundingClientRect().width));
    }
    function pages() { return Math.max(1, visible().length - perView() + 1); }
    function current() {
      var s = visible();
      if (!s.length) return 0;
      var w = s[0].getBoundingClientRect().width + parseFloat(getComputedStyle(track).columnGap || 0);
      return Math.round(track.scrollLeft / w);
    }
    function go(i) {
      var n = pages();
      i = (i + n) % n;
      var s = visible();
      if (!s[i]) return;
      track.scrollTo({ left: s[i].offsetLeft - track.offsetLeft, behavior: reduceMotion ? 'auto' : 'smooth' });
    }
    function buildDots() {
      if (!dotsWrap) return;
      dotsWrap.innerHTML = '';
      if (!active()) return;
      for (var i = 0; i < pages(); i++) {
        var b = document.createElement('button');
        b.type = 'button';
        b.setAttribute('aria-label', 'Go to slide ' + (i + 1));
        (function (k) { b.addEventListener('click', function () { stop(); go(k); }); })(i);
        dotsWrap.appendChild(b);
      }
      paint();
    }
    function paint() {
      if (!dotsWrap) return;
      var c = current();
      Array.prototype.forEach.call(dotsWrap.children, function (d, i) { d.classList.toggle('active', i === c); });
    }
    function stop() { touched = true; if (timer) clearInterval(timer); timer = null; }
    function start() {
      if (!auto || touched || reduceMotion || !active() || timer) return;
      timer = setInterval(function () { go(current() + 1); }, 4500);
    }

    if (prev) prev.addEventListener('click', function () { stop(); go(current() - 1); });
    if (next) next.addEventListener('click', function () { stop(); go(current() + 1); });
    track.addEventListener('scroll', function () { window.requestAnimationFrame(paint); }, { passive: true });
    ['touchstart', 'pointerdown', 'wheel'].forEach(function (ev) { track.addEventListener(ev, stop, { passive: true }); });

    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (en.isIntersecting) start();
          else if (timer) { clearInterval(timer); timer = null; }
        });
      }, { threshold: 0.4 }).observe(car);
    }
    var rt;
    window.addEventListener('resize', function () { clearTimeout(rt); rt = setTimeout(buildDots, 200); });
    buildDots();
  });

  /* ------------------------------------------------------------------
     FAQ: one open at a time
     ------------------------------------------------------------------ */
  document.querySelectorAll('.faq-list').forEach(function (list) {
    list.addEventListener('toggle', function (e) {
      if (!e.target.open) return;
      list.querySelectorAll('details[open]').forEach(function (d) { if (d !== e.target) d.open = false; });
    }, true);
  });

  /* ------------------------------------------------------------------
     Office hours + live open/closed status, computed in Arizona time
     (America/Phoenix — no daylight saving), not the visitor's timezone.
     Friday & Saturday run on alternate weeks, so they never show "open"
     with certainty — visitors are told to call to confirm.
     ------------------------------------------------------------------ */
  var HOURS = {             // [open, close] in 24h decimal; null = closed
    1: [7, 17], 2: [7, 18], 3: [7, 17], 4: [7, 18],
    5: [8, 15], 6: [8, 14], 0: null
  };
  var ALT_WEEK = { 5: true, 6: true };

  function azNow() {
    try {
      var parts = new Intl.DateTimeFormat('en-US', { timeZone: 'America/Phoenix', weekday: 'short', hour: 'numeric', minute: 'numeric', hour12: false }).formatToParts(new Date());
      var map = {};
      parts.forEach(function (p) { map[p.type] = p.value; });
      var days = { Sun: 0, Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6 };
      var h = parseInt(map.hour, 10) % 24;
      return { day: days[map.weekday], time: h + parseInt(map.minute, 10) / 60 };
    } catch (err) {
      var d = new Date();
      var utc = d.getUTCHours() + d.getUTCMinutes() / 60 - 7;
      var day = d.getUTCDay();
      if (utc < 0) { utc += 24; day = (day + 6) % 7; }
      return { day: day, time: utc };
    }
  }
  function fmt(h) {
    var hr = Math.floor(h), min = Math.round((h - hr) * 60);
    var ap = hr >= 12 ? 'pm' : 'am';
    var h12 = hr % 12 || 12;
    return h12 + (min ? ':' + (min < 10 ? '0' : '') + min : '') + ' ' + ap;
  }
  function nextOpening(now) {
    for (var i = 1; i <= 7; i++) {
      var d = (now.day + i) % 7;
      if (HOURS[d] && !ALT_WEEK[d]) {
        var names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
        return (i === 1 ? 'tomorrow' : names[d]) + ' at ' + fmt(HOURS[d][0]);
      }
    }
    return '';
  }

  var now = azNow();
  document.querySelectorAll('.hours tr[data-day]').forEach(function (tr) {
    if (parseInt(tr.dataset.day, 10) === now.day) tr.classList.add('today');
  });
  document.querySelectorAll('[data-status]').forEach(function (el) {
    var h = HOURS[now.day];
    var label = el.querySelector('.label');
    var open = h && now.time >= h[0] && now.time < h[1];
    var text;
    if (ALT_WEEK[now.day] && h && now.time < h[1]) {
      text = 'Open alternate ' + (now.day === 5 ? 'Fridays' : 'Saturdays') + ' ' + fmt(h[0]) + '–' + fmt(h[1]) + ' · call to confirm';
    } else if (open) {
      el.classList.add('open');
      text = 'Open now · until ' + fmt(h[1]);
    } else if (h && now.time < h[0] && !ALT_WEEK[now.day]) {
      text = 'Opens today at ' + fmt(h[0]);
    } else {
      text = 'Closed now · opens ' + nextOpening(now);
    }
    if (label) label.textContent = text;
  });

  /* ------------------------------------------------------------------
     Map fallback: if the embed can't load, an address card shows instead
     ------------------------------------------------------------------ */
  document.querySelectorAll('.map iframe').forEach(function (f) {
    f.addEventListener('load', function () { var fb = f.parentNode.querySelector('.map-fallback'); if (fb) fb.style.display = 'none'; });
  });

  /* Year in footer */
  document.querySelectorAll('[data-year]').forEach(function (el) { el.textContent = new Date().getFullYear(); });
})();
