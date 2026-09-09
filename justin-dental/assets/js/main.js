/* Justin Dental and Braces — landing page behaviour.
   No dependencies. Everything degrades gracefully if JS is off. */
(function () {
  'use strict';

  /* ----------------------------------------------------- ad tracking ---- */
  /* Fill these in before running traffic, then paste your GA4/GTM tags in
     the <head>. Events also go to dataLayer when gtag/GTM isn't present. */
  var ADS = {
    ga4MeasurementId:     '',   // GA4_MEASUREMENT_ID
    adsConversionId:      '',   // GOOGLE_ADS_CONVERSION_ID
    adsLabelCall:         '',   // GOOGLE_ADS_CONVERSION_LABEL (phone_click)
    adsLabelAppointment:  '',   // GOOGLE_ADS_CONVERSION_LABEL (appointment_click)
    gtmContainerId:       ''    // GTM_CONTAINER_ID
  };

  var CONVERSION_EVENTS = { phone_click: 'adsLabelCall', appointment_click: 'adsLabelAppointment' };

  function track(name) {
    if (typeof window.gtag === 'function') {
      window.gtag('event', name);
      var labelKey = CONVERSION_EVENTS[name];
      if (labelKey && ADS.adsConversionId && ADS[labelKey]) {
        window.gtag('event', 'conversion', { send_to: ADS.adsConversionId + '/' + ADS[labelKey] });
      }
    }
    (window.dataLayer = window.dataLayer || []).push({ event: name });
  }

  document.addEventListener('click', function (e) {
    var el = e.target.closest('[data-track]');
    if (el) track(el.getAttribute('data-track'));
  });

  /* --------------------------------------------------- sticky header ---- */
  var header = document.getElementById('header');
  if (header) {
    var stuck = false;
    var onScroll = function () {
      var should = window.scrollY > 8;
      if (should !== stuck) { stuck = should; header.classList.toggle('is-stuck', stuck); }
    };
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  /* ------------------------------------------------- scroll reveals ----- */
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var items = document.querySelectorAll('.reveal');
  if (reduced || !('IntersectionObserver' in window)) {
    items.forEach(function (el) { el.classList.add('is-in'); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) { entry.target.classList.add('is-in'); io.unobserve(entry.target); }
      });
    }, { rootMargin: '0px 0px -10% 0px', threshold: 0.08 });
    items.forEach(function (el) { io.observe(el); });
  }

  /* ------------------------------------- highlight today's office hours -- */
  /* Uses the practice's own timezone, not the visitor's. */
  var hoursList = document.getElementById('hours-list');
  if (hoursList) {
    var today;
    try {
      today = new Date().toLocaleDateString('en-US', { timeZone: 'America/Chicago', weekday: 'short' });
    } catch (err) {
      today = null;
    }
    if (today) {
      var dayIndex = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].indexOf(today.slice(0, 3));
      var todayRow = hoursList.querySelector('[data-day="' + dayIndex + '"]');
      if (todayRow) todayRow.classList.add('today');
    }
  }

  /* ----------------------------------------------- one accordion open --- */
  var faq = document.querySelectorAll('.faq__list details');
  faq.forEach(function (item) {
    item.addEventListener('toggle', function () {
      if (!item.open) return;
      faq.forEach(function (other) { if (other !== item) other.open = false; });
    });
  });

  /* --------------------------------------------------- floating desktop - */
  var floating = document.getElementById('floating-cta');
  var floatingClose = document.getElementById('floating-cta-close');
  if (floating) {
    var dismissed = false;
    try { dismissed = sessionStorage.getItem('jdb-float-dismissed') === '1'; } catch (e) {}
    if (dismissed) floating.classList.add('is-hidden');
    var revealFloating = function () {
      if (dismissed) return;
      if (window.scrollY > window.innerHeight * 0.6) floating.classList.add('is-visible');
    };
    revealFloating();
    window.addEventListener('scroll', revealFloating, { passive: true });
    if (floatingClose) {
      floatingClose.addEventListener('click', function () {
        floating.classList.add('is-hidden');
        dismissed = true;
        try { sessionStorage.setItem('jdb-float-dismissed', '1'); } catch (e) {}
      });
    }
  }

  /* ------------------------------------------------------ hero video ---- */
  /* Loads the background clip only on wider viewports and only when motion
     is welcome, so mobile visitors and prefers-reduced-motion users just get
     the static poster image -- never the ~640KB video download. */
  var heroMedia = document.getElementById('hero-media');
  var heroVideo = document.getElementById('hero-video');
  if (heroMedia && heroVideo) {
    var wideEnough = window.matchMedia('(min-width: 861px)').matches;
    if (wideEnough && !reduced) {
      [['assets/video/hero.webm', 'video/webm'], ['assets/video/hero.mp4', 'video/mp4']].forEach(function (pair) {
        var source = document.createElement('source');
        source.src = pair[0];
        source.type = pair[1];
        heroVideo.appendChild(source);
      });
      heroVideo.addEventListener('canplay', function () {
        heroMedia.classList.add('has-video');
      }, { once: true });
      heroVideo.load();
      var playPromise = heroVideo.play();
      if (playPromise && typeof playPromise.catch === 'function') {
        playPromise.catch(function () { /* autoplay blocked -- poster stays visible */ });
      }
    }
  }

  /* --------------------------------------------------------- footer ----- */
  var year = document.getElementById('year');
  if (year) year.textContent = new Date().getFullYear();
}());
