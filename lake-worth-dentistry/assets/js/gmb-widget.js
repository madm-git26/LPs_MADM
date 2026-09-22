/* ==========================================================================
   Lake Worth Dentistry — live Google rating & reviews widget
   Pulls real, current data from the Google Maps Platform Places API on every
   page load (no hardcoded number). Requires a Places-API-enabled key — see
   README.md "Live Google reviews widget" for setup. Fails open: if the key
   is missing or the API call fails for any reason, the page falls back to a
   plain "Read Reviews on Google" link instead of showing broken/fake data.
   ========================================================================== */
(function () {
  'use strict';

  var CONFIG = {
    // Paste a Places-API-enabled Google Maps Platform key here, restricted
    // (HTTP referrers) to this page's domain in Google Cloud Console.
    PLACES_API_KEY: '',
    PLACE_QUERY: 'Lake Worth Dentistry, 6427 Lake Worth Rd Ste B, Greenacres, FL 33463',
    MAX_REVIEWS: 3,
    CACHE_MINUTES: 60
  };

  function setText(selector, text) {
    document.querySelectorAll(selector).forEach(function (el) { el.textContent = text; });
  }

  function paintStars(el, rating) {
    var full = Math.round(rating);
    el.innerHTML = '';
    for (var i = 0; i < 5; i++) {
      var svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      var use = document.createElementNS('http://www.w3.org/2000/svg', 'use');
      use.setAttribute('href', '#i-star');
      svg.appendChild(use);
      if (i >= full) svg.style.opacity = '.3';
      el.appendChild(svg);
    }
  }

  function renderReviews(reviews) {
    var grids = document.querySelectorAll('[data-gmb-review-grid]');
    if (!grids.length || !reviews || !reviews.length) return;
    var top = reviews
      .filter(function (r) { return r.rating >= 4 && r.text; })
      .sort(function (a, b) { return (b.time || 0) - (a.time || 0); })
      .slice(0, CONFIG.MAX_REVIEWS);
    if (!top.length) return;

    grids.forEach(function (grid) {
      grid.innerHTML = '';
      top.forEach(function (r) {
        var card = document.createElement('article');
        card.className = 'review-card';

        var stars = document.createElement('span');
        stars.className = 'stars';
        stars.setAttribute('aria-hidden', 'true');
        paintStars(stars, r.rating);

        var quote = document.createElement('blockquote');
        quote.textContent = '“' + r.text + '”';

        var who = document.createElement('div');
        who.className = 'who';
        var avatar = document.createElement('span');
        avatar.className = 'avatar';
        avatar.setAttribute('aria-hidden', 'true');
        avatar.textContent = (r.author_name || '?').charAt(0).toUpperCase();
        var nameWrap = document.createElement('div');
        var strong = document.createElement('strong');
        strong.textContent = r.author_name || 'Google user';
        var span = document.createElement('span');
        span.textContent = 'Google review' + (r.relative_time_description ? ' · ' + r.relative_time_description : '');
        nameWrap.appendChild(strong);
        nameWrap.appendChild(span);
        who.appendChild(avatar);
        who.appendChild(nameWrap);

        card.appendChild(stars);
        card.appendChild(quote);
        card.appendChild(who);
        grid.appendChild(card);
      });
      grid.classList.add('is-loaded');
    });
  }

  function applyDetails(place) {
    if (!place) { fail('empty-place'); return; }
    if (typeof place.rating === 'number') {
      setText('[data-gmb-rating]', place.rating.toFixed(1));
      document.querySelectorAll('[data-gmb-stars]').forEach(function (el) { paintStars(el, place.rating); });
    }
    if (typeof place.user_ratings_total === 'number') {
      setText('[data-gmb-count]', place.user_ratings_total + '+');
    }
    setText('[data-gmb-status]', 'Live from Google — updated automatically');
    if (place.url) {
      document.querySelectorAll('[data-gmb-link]').forEach(function (a) { a.href = place.url; });
    }
    renderReviews(place.reviews);
    document.querySelectorAll('[data-gmb-widget]').forEach(function (el) { el.classList.add('is-loaded'); });
  }

  function fail() {
    setText('[data-gmb-status]', 'See our latest reviews on Google');
    document.querySelectorAll('[data-gmb-widget]').forEach(function (el) { el.classList.add('is-fallback'); });
  }

  function fromCache() {
    try {
      var raw = sessionStorage.getItem('gmb-place-cache-lakeworth');
      if (!raw) return null;
      var parsed = JSON.parse(raw);
      if (Date.now() - parsed.ts > CONFIG.CACHE_MINUTES * 60000) return null;
      return parsed.place;
    } catch (e) { return null; }
  }

  function toCache(place) {
    try { sessionStorage.setItem('gmb-place-cache-lakeworth', JSON.stringify({ ts: Date.now(), place: place })); } catch (e) { /* private mode etc — skip caching */ }
  }

  function loadPlaces() {
    if (!document.querySelector('[data-gmb-widget]')) return;
    if (!CONFIG.PLACES_API_KEY) { fail(); return; }

    var cached = fromCache();
    if (cached) { applyDetails(cached); return; }

    window.__gmbInit = function () {
      try {
        var svc = new google.maps.places.PlacesService(document.createElement('div'));
        svc.findPlaceFromQuery({ query: CONFIG.PLACE_QUERY, fields: ['place_id'] }, function (results, status) {
          if (status !== google.maps.places.PlacesServiceStatus.OK || !results || !results[0]) { fail(); return; }
          svc.getDetails({ placeId: results[0].place_id, fields: ['rating', 'user_ratings_total', 'reviews', 'url'] }, function (place, status2) {
            if (status2 !== google.maps.places.PlacesServiceStatus.OK || !place) { fail(); return; }
            var simplified = {
              rating: place.rating,
              user_ratings_total: place.user_ratings_total,
              url: place.url,
              reviews: (place.reviews || []).map(function (r) {
                return { author_name: r.author_name, rating: r.rating, text: r.text, relative_time_description: r.relative_time_description, time: r.time };
              })
            };
            toCache(simplified);
            applyDetails(simplified);
          });
        });
      } catch (e) { fail(); }
    };

    var script = document.createElement('script');
    script.src = 'https://maps.googleapis.com/maps/api/js?key=' + encodeURIComponent(CONFIG.PLACES_API_KEY) + '&libraries=places&callback=__gmbInit';
    script.async = true;
    script.onerror = fail;
    document.head.appendChild(script);
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', loadPlaces);
  else loadPlaces();
})();
