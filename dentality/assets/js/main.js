/* Dentality Family Dentistry — landing page behaviour.
   No dependencies. Everything degrades gracefully if JS is off. */
(function () {
  'use strict';

  /* ----------------------------------------------------- ad tracking ---- */
  /* Fill these in before running traffic, then paste your Google tag in the
     <head>. Events also go to dataLayer and fbq when those exist. */
  var ADS = {
    conversionId: '',   // e.g. 'AW-123456789'
    labelCall:    '',   // click-to-call conversion label
    labelBook:    ''    // book-online conversion label
  };

  var EVENTS = {
    call:       'click_to_call',
    book:       'click_book_online',
    directions: 'click_directions'
  };

  function track(kind) {
    var name = EVENTS[kind];
    if (!name) return;

    if (typeof window.gtag === 'function') {
      window.gtag('event', name);
      var label = kind === 'call' ? ADS.labelCall : kind === 'book' ? ADS.labelBook : '';
      if (ADS.conversionId && label) {
        window.gtag('event', 'conversion', { send_to: ADS.conversionId + '/' + label });
      }
    }
    if (typeof window.fbq === 'function') window.fbq('trackCustom', name);
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
      if (should !== stuck) {
        stuck = should;
        header.classList.toggle('is-stuck', stuck);
      }
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
        if (entry.isIntersecting) {
          entry.target.classList.add('is-in');
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -12% 0px', threshold: 0.08 });
    items.forEach(function (el) { io.observe(el); });
  }

  /* ------------------------------------- highlight today's office hours -- */
  /* Uses the practice's own timezone, not the visitor's. */
  var list = document.getElementById('hours-list');
  if (list) {
    var day;
    try {
      day = new Date().toLocaleDateString('en-US', {
        timeZone: 'America/Chicago', weekday: 'short'
      });
    } catch (err) {
      day = null;
    }
    if (day) {
      var index = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].indexOf(day.slice(0, 3));
      var row = list.querySelector('[data-day="' + index + '"]');
      if (row) row.classList.add('today');
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

  /* --------------------------------------------------------- footer ----- */
  var year = document.getElementById('year');
  if (year) year.textContent = new Date().getFullYear();
}());
