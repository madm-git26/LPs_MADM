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
    adsLabelAppointment:  '',   // GOOGLE_ADS_CONVERSION_LABEL (appointment_click / form_submit)
    gtmContainerId:       ''    // GTM_CONTAINER_ID
  };

  var CONVERSION_EVENTS = { phone_click: 'adsLabelCall', appointment_click: 'adsLabelAppointment', form_submit: 'adsLabelAppointment' };

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

  /* ----------------------------------------------- one accordion open --- */
  var faq = document.querySelectorAll('.faq-list details');
  faq.forEach(function (item) {
    item.addEventListener('toggle', function () {
      if (!item.open) return;
      faq.forEach(function (other) { if (other !== item) other.open = false; });
    });
  });

  /* --------------------------------------------------- appointment form - */
  var form = document.getElementById('appt-form');
  var success = document.getElementById('form-success');
  if (form && success) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!form.checkValidity()) { form.reportValidity(); return; }
      /* No backend is wired up yet -- see README "Needs verification before
         launch". Point this at the practice's real form endpoint (Gravity
         Forms, a CRM webhook, etc.) before this goes live; for now it just
         confirms receipt in the browser so the UI can be reviewed end to end. */
      track('form_submit');
      form.hidden = true;
      success.classList.add('is-shown');
      success.setAttribute('tabindex', '-1');
      success.focus();
    });
  }

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

  /* --------------------------------------------------------- footer ----- */
  var year = document.getElementById('year');
  if (year) year.textContent = new Date().getFullYear();
}());
