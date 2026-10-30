/* Belmont Dentistry Paradise Valley — motion layer.
   Runs after lp.js (which handles tracking, carousels, reveals, hours and video).
   Adds: scroll progress, sliding headline words, floating 3D rings, button
   ripple + magnetic pull, count-up stats, parallax backgrounds, a gentle hero
   scroll effect and the before/after smile sliders. Respects reduced motion. */
(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var finePointer = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
  var desktop = function () { return window.matchMedia('(min-width: 1025px)').matches; };

  /* ---------------------------------------------------------------
     Headline: wrap every word so it can slide up into place
     --------------------------------------------------------------- */
  document.querySelectorAll('h1[data-split]').forEach(function (h1) {
    if (reduceMotion) return;
    var i = 0;
    function wrap(node) {
      Array.prototype.slice.call(node.childNodes).forEach(function (child) {
        if (child.nodeType === 3) {
          var frag = document.createDocumentFragment();
          child.textContent.split(/(\s+)/).forEach(function (part) {
            if (!part) return;
            if (/^\s+$/.test(part)) { frag.appendChild(document.createTextNode(' ')); return; }
            var outer = document.createElement('span');
            outer.className = 'w';
            var inner = document.createElement('span');
            inner.textContent = part;
            inner.style.setProperty('--i', i++);
            outer.appendChild(inner);
            inner.addEventListener('animationend', function () { outer.classList.add('done'); });
            frag.appendChild(outer);
          });
          child.parentNode.replaceChild(frag, child);
        } else if (child.nodeType === 1) {
          wrap(child);
        }
      });
    }
    h1.setAttribute('aria-label', h1.textContent.replace(/\s+/g, ' ').trim());
    wrap(h1);
  });

  /* ---------------------------------------------------------------
     Floating 3D rings behind the hero card (desktop)
     --------------------------------------------------------------- */
  var hero = document.querySelector('.hero');
  if (hero && !reduceMotion && hero.querySelector('.hero-card')) {
    var orbit = document.createElement('div');
    orbit.className = 'orbit';
    orbit.setAttribute('aria-hidden', 'true');
    orbit.innerHTML = '<span></span><span></span><span></span>';
    hero.insertBefore(orbit, hero.querySelector('.hero-grid'));
  }

  /* ---------------------------------------------------------------
     Scroll-linked effects: progress bar, parallax, hero fade
     --------------------------------------------------------------- */
  var bar = document.querySelector('.scroll-progress span');
  var layers = Array.prototype.slice.call(document.querySelectorAll('[data-parallax]'));
  var heroCopy = document.querySelector('.hero-copy');
  var heroMedia = document.querySelector('.hero-media');
  var ticking = false;

  function onScroll() {
    var y = window.scrollY;
    var max = document.documentElement.scrollHeight - window.innerHeight;
    if (bar) bar.style.setProperty('--p', max > 0 ? Math.min(1, y / max).toFixed(4) : 0);
    if (!reduceMotion) {
      var vh = window.innerHeight;
      var strength = desktop() ? 0.18 : 0.08;
      layers.forEach(function (el) {
        var r = el.parentNode.getBoundingClientRect();
        if (r.bottom < -100 || r.top > vh + 100) return;
        var offset = (r.top + r.height / 2 - vh / 2) * -strength;
        el.style.transform = 'translate3d(0,' + offset.toFixed(1) + 'px,0)';
      });
      if (hero && desktop() && y < vh * 1.2) {
        if (heroCopy) {
          heroCopy.style.transform = 'translate3d(0,' + (y * 0.22).toFixed(1) + 'px,0)';
          heroCopy.style.opacity = Math.max(0, 1 - y / (vh * 0.9)).toFixed(3);
        }
        if (heroMedia) heroMedia.style.transform = 'scale(' + (1 + y * 0.00025).toFixed(4) + ')';
      }
    }
    ticking = false;
  }
  window.addEventListener('scroll', function () {
    if (!ticking) { ticking = true; window.requestAnimationFrame(onScroll); }
  }, { passive: true });
  window.addEventListener('resize', onScroll);
  onScroll();

  /* ---------------------------------------------------------------
     Buttons: click ripple everywhere, magnetic pull on desktop
     --------------------------------------------------------------- */
  document.addEventListener('pointerdown', function (e) {
    var btn = e.target.closest && e.target.closest('.btn');
    if (!btn || reduceMotion) return;
    var r = btn.getBoundingClientRect();
    var dot = document.createElement('span');
    dot.className = 'ripple';
    dot.style.left = (e.clientX - r.left) + 'px';
    dot.style.top = (e.clientY - r.top) + 'px';
    btn.appendChild(dot);
    setTimeout(function () { dot.remove(); }, 700);
  });

  if (finePointer && !reduceMotion) {
    document.querySelectorAll('.btn-lg').forEach(function (btn) {
      btn.classList.add('magnet');
      btn.addEventListener('mousemove', function (e) {
        var r = btn.getBoundingClientRect();
        var x = (e.clientX - r.left - r.width / 2) / r.width;
        var y = (e.clientY - r.top - r.height / 2) / r.height;
        btn.style.transform = 'translate(' + (x * 10).toFixed(1) + 'px,' + (y * 8 - 3).toFixed(1) + 'px)';
      });
      btn.addEventListener('mouseleave', function () { btn.style.transform = ''; });
    });
  }

  /* ---------------------------------------------------------------
     Count-up numbers in the stats bar
     --------------------------------------------------------------- */
  var counters = document.querySelectorAll('[data-count]');
  function countUp(el) {
    var target = parseFloat(el.dataset.count);
    var decimals = parseInt(el.dataset.decimals || '0', 10);
    var start = null;
    var dur = 1400;
    function step(ts) {
      if (!start) start = ts;
      var k = Math.min(1, (ts - start) / dur);
      var eased = 1 - Math.pow(1 - k, 3);
      el.textContent = (target * eased).toFixed(decimals);
      if (k < 1) window.requestAnimationFrame(step);
    }
    window.requestAnimationFrame(step);
  }
  if ('IntersectionObserver' in window && !reduceMotion) {
    var co = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { countUp(en.target); co.unobserve(en.target); }
      });
    }, { threshold: 0.6 });
    counters.forEach(function (el) { co.observe(el); });
  }

  /* ---------------------------------------------------------------
     Before / after sliders — drag (range input), plus a one-time
     hint sweep when each first comes into view
     --------------------------------------------------------------- */
  document.querySelectorAll('.ba').forEach(function (fig) {
    var range = fig.querySelector('.ba-range');
    if (!range) return;
    function set(v) { fig.style.setProperty('--pos', v + '%'); }
    range.addEventListener('input', function () { set(range.value); });
    var touched = false;
    range.addEventListener('pointerdown', function () { touched = true; });
    if (!reduceMotion && 'IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (en) {
          if (!en.isIntersecting) return;
          io.disconnect();
          var t0 = null;
          (function sweep(ts) {
            if (touched) return;
            if (!t0) t0 = ts;
            var k = (ts - t0) / 1800;
            if (k >= 1) { set(50); range.value = 50; return; }
            var v = 50 + Math.sin(k * Math.PI * 2) * 28;
            set(v.toFixed(1)); range.value = v;
            window.requestAnimationFrame(sweep);
          })(performance.now());
        });
      }, { threshold: 0.7 });
      io.observe(fig);
    }
  });
})();
