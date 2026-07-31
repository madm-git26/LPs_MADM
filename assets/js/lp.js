/* ==========================================================================
   Everything Teeth Family Dental — Landing Page behaviour
   - Google Ads / GA4 conversion event hooks
   - Hero clinic video: autoplay with a graceful play/pause fallback
   - "Open now" + today's-hours highlighting
   ========================================================================== */
(function () {
  'use strict';

  /* ------------------------------------------------------------------
     CONFIG — paste your Google Ads conversion labels here.
     Get them from Google Ads > Goals > Conversions > (your action).
     ------------------------------------------------------------------ */
  var CONFIG = {
    PHONE_E164: '+13054046659',
    ADS_CONVERSION_ID: '',   // e.g. 'AW-123456789'
    LABEL_CALL: '',          // click-to-call conversion label
    LABEL_BOOK: ''           // book-online click conversion label
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
          window.gtag('event', 'conversion', {
            send_to: CONFIG.ADS_CONVERSION_ID + '/' + label
          });
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
    else if (href.indexOf('book.modento.io') > -1) track('click_book_online', CONFIG.LABEL_BOOK);
    else if (href.indexOf('maps') > -1 || href.indexOf('goo.gl') > -1) track('click_directions', '');
  });

  /* ------------------------- hours logic -------------------------- */
  // Mon 1, Tue 2 … Sun 0.  [openMinutes, closeMinutes] or null when closed.
  var HOURS = {
    1: [630, 1110],  // Monday    10:30 am – 6:30 pm
    2: null,         // Tuesday   closed
    3: [630, 1110],  // Wednesday 10:30 am – 6:30 pm
    4: [630, 1110],  // Thursday  10:30 am – 6:30 pm
    5: [450, 930],   // Friday     7:30 am – 3:30 pm
    6: null,         // Saturday  closed
    0: null          // Sunday    closed
  };

  function miamiNow() {
    // Evaluate against the clinic's local time, not the visitor's.
    var parts = new Intl.DateTimeFormat('en-US', {
      timeZone: 'America/New_York',
      weekday: 'short', hour: 'numeric', minute: 'numeric', hour12: false
    }).formatToParts(new Date());
    var map = {};
    parts.forEach(function (p) { map[p.type] = p.value; });
    var days = { Sun: 0, Mon: 1, Tue: 2, Wed: 3, Thu: 4, Fri: 5, Sat: 6 };
    return {
      day: days[map.weekday],
      minutes: parseInt(map.hour, 10) * 60 + parseInt(map.minute, 10)
    };
  }

  function initHours() {
    var now;
    try { now = miamiNow(); } catch (e) { return; }

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

  /* ---------------------- hero clinic video -----------------------
     The markup carries no `autoplay` attribute. Playback starts only when the
     video is on screen, so a phone visitor who never scrolls past the headline
     never downloads the file. If the visitor pauses it by hand, we leave it
     paused — scrolling away and back will not override that choice.
     ---------------------------------------------------------------- */
  function initVideo() {
    var video = document.querySelector('.clinic-video');
    var toggle = document.querySelector('.video-toggle');
    if (!video) return;

    // Honour a reduced-motion preference: hold on the poster until asked.
    var reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var userPaused = reduced;

    function paint() {
      if (!toggle) return;
      var paused = video.paused;
      toggle.classList.toggle('is-paused', paused);
      toggle.setAttribute('aria-label', paused
        ? (toggle.getAttribute('data-label-play') || 'Play video')
        : (toggle.getAttribute('data-label-pause') || 'Pause video'));
    }

    function play() {
      var p = video.play();
      if (p && p.catch) p.catch(paint);   // blocked? the poster simply stays up
    }

    video.addEventListener('play', paint);
    video.addEventListener('pause', paint);

    if (toggle) {
      toggle.addEventListener('click', function () {
        if (video.paused) { userPaused = false; play(); }
        else { userPaused = true; video.pause(); }
      });
    }

    if ('IntersectionObserver' in window) {
      new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            if (!userPaused && video.paused) play();
          } else if (!video.paused) {
            video.pause();   // off screen: stop spending battery and data
          }
        });
      }, { threshold: 0.25 }).observe(video);
    } else if (!reduced) {
      play();   // no IntersectionObserver: fall back to playing straight away
    }

    paint();
  }

  /* ----------------------------- boot ----------------------------- */
  function boot() {
    initHours();
    initVideo();

    // Smooth-scroll for in-page anchors (respects reduced-motion via CSS).
    document.querySelectorAll('a[href^="#"]').forEach(function (a) {
      a.addEventListener('click', function (e) {
        var id = a.getAttribute('href');
        if (!id || id === '#') return;
        var target = document.querySelector(id);
        if (!target) return;
        e.preventDefault();
        var top = target.getBoundingClientRect().top + window.pageYOffset - 90;
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
