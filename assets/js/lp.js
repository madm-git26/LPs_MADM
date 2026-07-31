/* ==========================================================================
   Everything Teeth Family Dental — Landing Page behaviour
   - Appointment form validation + submission
   - Google Ads / GA4 conversion event hooks
   - "Open now" + today's-hours highlighting
   ========================================================================== */
(function () {
  'use strict';

  /* ------------------------------------------------------------------
     CONFIG — set FORM_ENDPOINT to the practice's form handler.
     Works with Formspree, HubSpot, Zapier catch-hooks, or a custom URL.
     While it is empty the form falls back to a mailto-free "call us"
     confirmation so no lead is ever silently lost.
     ------------------------------------------------------------------ */
  var CONFIG = {
    FORM_ENDPOINT: '',                       // e.g. 'https://formspree.io/f/xxxxxxx'
    PHONE_E164: '+13054046659',
    // Google Ads conversion labels — paste from Google Ads > Conversions
    ADS_CONVERSION_ID: '',                   // e.g. 'AW-123456789'
    LABEL_CALL: '',                          // e.g. 'abcDEFghIJKlmnOP'
    LABEL_FORM: '',
    LABEL_BOOK: ''
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
      var shutText = el.getAttribute('data-closed-text') || 'Closed right now — leave us a message';
      el.textContent = isOpen ? openText : shutText;
      el.classList.toggle('is-open', isOpen);
    });
  }

  /* --------------------------- the form --------------------------- */
  function showError(field, message) {
    field.classList.add('has-error');
    var input = field.querySelector('input, select, textarea');
    if (input) input.setAttribute('aria-invalid', 'true');
    var err = field.querySelector('.err');
    if (err && message) err.textContent = message;
  }

  function clearError(field) {
    field.classList.remove('has-error');
    var input = field.querySelector('input, select, textarea');
    if (input) input.removeAttribute('aria-invalid');
  }

  function validPhone(value) {
    return (value.replace(/\D/g, '').length >= 10);
  }

  function initForm(form) {
    var statusBox = form.querySelector('.form-status');
    var submitBtn = form.querySelector('[type="submit"]');
    var strings = {
      required: form.getAttribute('data-msg-required') || 'This field is required.',
      phone:    form.getAttribute('data-msg-phone')    || 'Please enter a valid phone number.',
      email:    form.getAttribute('data-msg-email')    || 'Please enter a valid email address.',
      ok:       form.getAttribute('data-msg-ok')       || 'Thank you! Your request has been received — our team will call you shortly to confirm your appointment.',
      fallback: form.getAttribute('data-msg-fallback') || 'Thanks! To lock in the soonest appointment, please call us now at (305) 404-6659.',
      sending:  form.getAttribute('data-msg-sending')  || 'Sending…',
      submit:   submitBtn ? submitBtn.textContent : ''
    };

    form.querySelectorAll('input, select, textarea').forEach(function (input) {
      input.addEventListener('input', function () {
        var field = input.closest('.field');
        if (field) clearError(field);
      });
    });

    form.addEventListener('submit', function (e) {
      e.preventDefault();

      // Honeypot — silently accept and discard bot submissions.
      var hp = form.querySelector('.hp-field input');
      if (hp && hp.value) return;

      var ok = true;
      form.querySelectorAll('.field').forEach(function (field) {
        var input = field.querySelector('input, select, textarea');
        if (!input || !input.required) return;
        var value = (input.value || '').trim();

        if (!value) { showError(field, strings.required); ok = false; return; }
        if (input.type === 'tel' && !validPhone(value)) { showError(field, strings.phone); ok = false; return; }
        if (input.type === 'email' && !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(value)) {
          showError(field, strings.email); ok = false; return;
        }
        clearError(field);
      });

      if (!ok) {
        var firstBad = form.querySelector('.field.has-error input, .field.has-error select, .field.has-error textarea');
        if (firstBad) firstBad.focus();
        return;
      }

      function say(message, isError) {
        if (!statusBox) return;
        statusBox.textContent = message;
        statusBox.classList.add('is-visible');
        statusBox.classList.toggle('is-error', !!isError);
      }

      track('appointment_form_submit', CONFIG.LABEL_FORM);

      if (!CONFIG.FORM_ENDPOINT) {
        // No endpoint wired up yet — never drop the lead, route it to the phone.
        say(strings.fallback, false);
        form.reset();
        return;
      }

      if (submitBtn) { submitBtn.disabled = true; submitBtn.textContent = strings.sending; }

      var payload = new FormData(form);
      payload.append('page', document.body.getAttribute('data-lp') || '');
      payload.append('page_url', window.location.href);

      fetch(CONFIG.FORM_ENDPOINT, {
        method: 'POST',
        body: payload,
        headers: { Accept: 'application/json' }
      })
        .then(function (res) {
          if (!res.ok) throw new Error('bad status');
          say(strings.ok, false);
          form.reset();
        })
        .catch(function () {
          say(strings.fallback, true);
        })
        .then(function () {
          if (submitBtn) { submitBtn.disabled = false; submitBtn.textContent = strings.submit; }
        });
    });
  }

  /* ----------------------------- boot ----------------------------- */
  function boot() {
    initHours();
    document.querySelectorAll('form[data-lp-form]').forEach(initForm);

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
