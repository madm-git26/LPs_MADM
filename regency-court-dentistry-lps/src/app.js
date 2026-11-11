(function(){
  'use strict';
  /* ---------- CONFIG: optional direct Google Ads conversion labels (GTM handles the rest) ---------- */
  var CONFIG = { ADS_ID:'', LABEL_CALL:'', LABEL_BOOK:'' };
  var LP = document.body.getAttribute('data-lp') || 'regency-court';
  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var finePointer = window.matchMedia('(hover:hover) and (pointer:fine)').matches;
  function $$(s,c){ return [].slice.call((c||document).querySelectorAll(s)); }

  /* ---------- Conversion tracking → dataLayer (GTM-N394H9F) ---------- */
  function track(name,label,extra){
    try{
      window.dataLayer = window.dataLayer || [];
      var o = {event:name, lp:LP}; if (extra) for (var k in extra) o[k]=extra[k];
      window.dataLayer.push(o);
      if (typeof window.gtag==='function' && CONFIG.ADS_ID && label) window.gtag('event','conversion',{send_to:CONFIG.ADS_ID+'/'+label});
    }catch(e){}
  }
  document.addEventListener('click', function(e){
    var a = e.target.closest && e.target.closest('a'); if(!a) return;
    var h = a.getAttribute('href')||'';
    var z = a.closest('section[id],header,nav,aside,.alertbar,.fab,.exit'), where = z ? (z.id || z.className.split(' ')[0]) : '';
    if (h.indexOf('tel:')===0) track('click_to_call', CONFIG.LABEL_CALL, {cta_zone:where||''});
    else if (h.indexOf('book.allinone.dental')>-1) track('click_book_online', CONFIG.LABEL_BOOK, {cta_zone:where||''});
    else if (h.indexOf('maps')>-1) track('click_directions','');
  });

  /* ---------- Tap ripple on buttons ---------- */
  document.addEventListener('pointerdown', function(e){
    var b = e.target.closest && e.target.closest('.btn'); if(!b || reduced) return;
    var r = b.getBoundingClientRect(), s = Math.max(r.width,r.height), sp = document.createElement('span');
    sp.className='rip'; sp.style.width=sp.style.height=s+'px';
    sp.style.left=(e.clientX-r.left-s/2)+'px'; sp.style.top=(e.clientY-r.top-s/2)+'px';
    b.appendChild(sp); setTimeout(function(){ sp.remove(); },700);
  });

  /* ---------- Header shrink + scroll progress ---------- */
  var header = document.querySelector('.header'), bar = document.querySelector('.progress'), fab = document.querySelector('.fab');
  function onScroll(){
    var y = window.scrollY, h = document.documentElement.scrollHeight - innerHeight;
    if (header) header.classList.toggle('is-scrolled', y > 40);
    if (bar) bar.style.width = (h>0 ? (y/h*100) : 0) + '%';
    if (fab) fab.classList.toggle('on', y > innerHeight*0.8);
  }
  addEventListener('scroll', onScroll, {passive:true}); onScroll();

  /* ---------- Reveal on scroll ---------- */
  var rvs = $$('.rv');
  rvs.forEach(function(el){ var d = el.getAttribute('data-d'); if (d) el.style.transitionDelay = (d*0.09)+'s'; });
  if ('IntersectionObserver' in window && !reduced){
    var io = new IntersectionObserver(function(es){
      es.forEach(function(en){ if(en.isIntersecting){ en.target.classList.add('in'); io.unobserve(en.target); } });
    }, {threshold:.12, rootMargin:'0px 0px -40px 0px'});
    rvs.forEach(function(el){ io.observe(el); });
    var sio = new IntersectionObserver(function(es){ es.forEach(function(en){ if(en.isIntersecting){ en.target.classList.add('in-view'); sio.unobserve(en.target);} }); },{threshold:.3});
    $$('.steps').forEach(function(el){ sio.observe(el); });
  } else { rvs.forEach(function(el){ el.classList.add('in'); }); $$('.steps').forEach(function(el){ el.classList.add('in-view'); }); }

  /* ---------- Count-up numbers ---------- */
  function countUp(el){
    var to = parseFloat(el.getAttribute('data-count')), from = parseFloat(el.getAttribute('data-start')||0),
        dec = parseInt(el.getAttribute('data-dec')||0,10), sep = el.hasAttribute('data-sep'), t0 = null, dur = 1600;
    function fmt(v){ var s=v.toFixed(dec); return sep ? s.replace(/\B(?=(\d{3})+(?!\d))/g, ',') : s; }
    function step(t){ if(!t0) t0=t; var p=Math.min((t-t0)/dur,1), e=1-Math.pow(1-p,3);
      el.textContent = fmt(from+(to-from)*e); if(p<1) requestAnimationFrame(step); }
    requestAnimationFrame(step);
  }
  if ('IntersectionObserver' in window && !reduced){
    var cio = new IntersectionObserver(function(es){ es.forEach(function(en){ if(en.isIntersecting){ countUp(en.target); cio.unobserve(en.target);} }); },{threshold:.6});
    $$('[data-count]').forEach(function(el){ cio.observe(el); });
  }

  /* ---------- Hero word rotator ---------- */
  var rot = document.querySelector('[data-rotate]');
  if (rot && !reduced){
    var words = rot.children, wi = 0;
    setInterval(function(){
      var cur = words[wi]; cur.classList.remove('on'); cur.classList.add('out');
      wi = (wi+1) % words.length; var nx = words[wi]; nx.classList.remove('out');
      void nx.offsetWidth; nx.classList.add('on');
      setTimeout(function(){ cur.classList.remove('out'); }, 600);
    }, 2400);
  }

  /* ---------- Hero backdrop slideshow (Ken Burns crossfade) ---------- */
  var slides = $$('.hero-bg .sl'), sdots = document.querySelector('.slide-dots');
  if (slides.length){
    // lazy-load all but the first slide after the page has loaded
    addEventListener('load', function(){ slides.forEach(function(s){ var b=s.getAttribute('data-bg'); if(b) s.style.backgroundImage='url("'+b+'")'; }); });
    if (sdots) slides.forEach(function(_,k){ var i=document.createElement('i'); if(!k) i.className='on'; sdots.appendChild(i); });
    if (slides.length>1 && !reduced){
      var si = 0;
      setInterval(function(){
        if (document.visibilityState!=='visible') return;
        slides[si].classList.remove('on'); if (sdots) sdots.children[si].classList.remove('on');
        si = (si+1) % slides.length;
        var n = slides[si]; n.classList.remove('on'); void n.offsetWidth; n.classList.add('on');
        if (sdots) sdots.children[si].classList.add('on');
      }, 6500);
    }
  }

  /* ---------- Desktop 3D: card tilt, hero parallax, magnetic CTAs ---------- */
  if (finePointer && !reduced){
    $$('[data-tilt]').forEach(function(el){
      el.addEventListener('mousemove', function(e){
        var r = el.getBoundingClientRect(), x = (e.clientX-r.left)/r.width-.5, y = (e.clientY-r.top)/r.height-.5;
        el.style.transition = 'transform .1s linear';
        el.style.transform = 'perspective(900px) rotateX('+(-y*7)+'deg) rotateY('+(x*9)+'deg) translateY(-6px)';
      });
      el.addEventListener('mouseleave', function(){
        el.style.transition = 'transform .7s cubic-bezier(.22,1,.36,1)'; el.style.transform = '';
      });
    });
    var hero = document.querySelector('.hero'), orbs = $$('.hero .orb');
    if (hero) hero.addEventListener('mousemove', function(e){
      var x = e.clientX/innerWidth-.5, y = e.clientY/innerHeight-.5;
      orbs.forEach(function(o,k){ o.style.translate = (x*(k?-40:40))+'px '+(y*(k?-30:30))+'px'; });
    });
    $$('[data-magnetic]').forEach(function(b){
      b.addEventListener('mousemove', function(e){
        var r = b.getBoundingClientRect(), x = e.clientX-r.left-r.width/2, y = e.clientY-r.top-r.height/2;
        b.style.transform = 'translate('+(x*.12)+'px,'+(y*.22-3)+'px)';
      });
      b.addEventListener('mouseleave', function(){ b.style.transform=''; });
    });
  }

  /* ---------- Tabs ---------- */
  $$('[role="tablist"]').forEach(function(list){
    var tabs = $$('[role="tab"]', list);
    tabs.forEach(function(t){
      t.addEventListener('click', function(){
        tabs.forEach(function(o){ o.setAttribute('aria-selected','false'); var p=document.getElementById(o.getAttribute('aria-controls')); p.classList.remove('on'); p.hidden=true; });
        t.setAttribute('aria-selected','true');
        var p = document.getElementById(t.getAttribute('aria-controls')); p.hidden=false; p.classList.add('on');
        if (innerWidth<1024) t.scrollIntoView({behavior:reduced?'auto':'smooth', block:'nearest', inline:'center'});
      });
    });
  });

  /* ---------- Carousels (scroll-snap + dots + arrows + autoplay) ---------- */
  $$('[data-carousel]').forEach(function(c){
    var track = c.querySelector('.track, .track-m'); if(!track) return;
    var items = track.children, dots = c.querySelector('.dots');
    var prev = c.querySelector('[data-prev]'), next = c.querySelector('[data-next]');
    function step(){ return items.length>1 ? items[1].offsetLeft - items[0].offsetLeft : track.clientWidth; }
    function idx(){ return Math.round(track.scrollLeft / step()); }
    if (dots){
      for (var k=0;k<items.length;k++){ (function(k){ var b=document.createElement('button'); b.type='button'; b.tabIndex=-1; b.setAttribute('aria-label','Go to slide '+(k+1));
        b.addEventListener('click',function(){ track.scrollTo({left:k*step(),behavior:'smooth'}); }); dots.appendChild(b); })(k); }
    }
    function paint(){ if(!dots) return; var n=idx(); [].forEach.call(dots.children,function(d,j){ d.classList.toggle('on', j===n); }); }
    track.addEventListener('scroll', function(){ requestAnimationFrame(paint); }, {passive:true}); paint();
    function go(dir){
      var max = track.scrollWidth - track.clientWidth - 4;
      if (dir>0 && track.scrollLeft >= max) track.scrollTo({left:0,behavior:'smooth'});
      else track.scrollBy({left:dir*step(),behavior:'smooth'});
    }
    if (prev) prev.addEventListener('click', function(){ go(-1); });
    if (next) next.addEventListener('click', function(){ go(1); });
    var auto = parseInt(c.getAttribute('data-auto')||0,10);
    if (auto && !reduced){
      var timer, hold=false, seen=false;
      if ('IntersectionObserver' in window) new IntersectionObserver(function(es){ seen = es[0].isIntersecting; }).observe(c);
      c.addEventListener('mouseenter',function(){hold=true}); c.addEventListener('mouseleave',function(){hold=false});
      c.addEventListener('touchstart',function(){hold=true; clearTimeout(timer); timer=setTimeout(function(){hold=false},7000);},{passive:true});
      setInterval(function(){ if(!hold && seen && document.visibilityState==='visible' && track.scrollWidth>track.clientWidth+4) go(1); }, auto);
    }
  });

  /* ---------- Gallery lightbox ---------- */
  var lb = document.querySelector('.lightbox');
  if (lb){
    var lbImg = lb.querySelector('img');
    $$('[data-full]').forEach(function(f){
      f.addEventListener('click', function(){ lbImg.src = f.getAttribute('data-full'); lbImg.alt = f.querySelector('img').alt; lb.classList.add('on'); });
    });
    lb.addEventListener('click', function(e){ if (e.target!==lbImg) lb.classList.remove('on'); });
    addEventListener('keydown', function(e){ if (e.key==='Escape') lb.classList.remove('on'); });
  }

  /* ---------- Insurance checker ---------- */
  var insOut = document.querySelector('[data-ins-out]');
  $$('.carrier').forEach(function(b){
    b.addEventListener('click', function(){
      $$('.carrier').forEach(function(o){ o.setAttribute('aria-pressed','false'); });
      b.setAttribute('aria-pressed','true');
      var name = b.getAttribute('data-name') || b.textContent;
      var msg = insOut.querySelector('p');
      msg.innerHTML = name==='none'
        ? '<b>No insurance? No problem.</b> New patients can start with our <b>$69 exam &amp; X-rays</b> special, and CareCredit&reg; financing keeps treatment affordable.'
        : 'Have <b>'+name+'</b>? Call <b>{{PHONE}}</b> &mdash; we&rsquo;ll check your <b>'+name+'</b> benefits in minutes and file the claim for you.';
      var box = insOut.parentNode; box.classList.remove('swap'); void box.offsetWidth; box.classList.add('swap');
      track('insurance_check','',{carrier:name});
    });
  });

  /* ---------- Emergency triage picker ---------- */
  var triOut = document.querySelector('[data-tri-out]');
  $$('.tri-opt').forEach(function(b){
    b.addEventListener('click', function(){
      $$('.tri-opt').forEach(function(o){ o.setAttribute('aria-pressed','false'); });
      b.setAttribute('aria-pressed','true');
      var tpl = document.querySelector('template[data-tri-for="'+b.getAttribute('data-tri')+'"]');
      if (tpl && triOut){ triOut.innerHTML = tpl.innerHTML; var box=triOut.parentNode; box.classList.remove('swap'); void box.offsetWidth; box.classList.add('swap'); }
      track('triage_select','',{emergency:b.getAttribute('data-tri')});
    });
  });

  /* ---------- Exit-intent call prompt (emergency, desktop, once per session) ---------- */
  var exitEl = document.querySelector('.exit');
  if (exitEl && finePointer){
    var shown = false; try{ shown = sessionStorage.getItem('rc_exit')==='1'; }catch(e){}
    document.addEventListener('mouseout', function(e){
      if (shown || e.relatedTarget || e.clientY > 8 || scrollY < 400) return;
      shown = true; try{ sessionStorage.setItem('rc_exit','1'); }catch(err){}
      exitEl.classList.add('on'); track('exit_prompt_shown','');
    });
    exitEl.addEventListener('click', function(e){ if (e.target===exitEl || e.target.closest('.x')) exitEl.classList.remove('on'); });
    addEventListener('keydown', function(e){ if (e.key==='Escape') exitEl.classList.remove('on'); });
  }

  /* ---------- Office hours + live open/closed (Boca Raton = America/New_York) ---------- */
  var HOURS = {1:[480,1020],2:[480,1020],3:[480,1020],4:[480,1020],5:[480,1020],6:[480,840],0:null};
  var NAMES = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];
  function fmt(m){ var h=Math.floor(m/60), mm=m%60, ap=h>=12?'pm':'am'; h=h%12||12; return h+(mm?':'+(mm<10?'0':'')+mm:'')+' '+ap; }
  try{
    var parts = new Intl.DateTimeFormat('en-US',{timeZone:'America/New_York',weekday:'short',hour:'numeric',minute:'numeric',hour12:false}).formatToParts(new Date()), m={};
    parts.forEach(function(p){ m[p.type]=p.value; });
    var day = {Sun:0,Mon:1,Tue:2,Wed:3,Thu:4,Fri:5,Sat:6}[m.weekday], mins = (parseInt(m.hour,10)%24)*60 + parseInt(m.minute,10);
    var span = HOURS[day], open = !!span && mins>=span[0] && mins<span[1], txt, urg;
    if (open){
      txt = 'Open now · until ' + fmt(span[1]);
      urg = mins > span[1]-120 ? 'We close at '+fmt(span[1])+' today — call now to be seen' : 'Open now — call for a same-day emergency visit';
    } else {
      var d = day, add = 0, s;
      if (span && mins < span[0]) s = span; else { do { d=(d+1)%7; add++; s=HOURS[d]; } while(!s && add<7); }
      var when = (add===0?'today':(add===1?'tomorrow':NAMES[d])) + ' at ' + fmt(s[0]);
      txt = 'Closed now · opens ' + when;
      urg = 'Call now to reserve the first emergency slot ' + when;
    }
    $$('[data-live-text]').forEach(function(el){ el.textContent = txt; });
    $$('[data-urgency]').forEach(function(el){ el.textContent = urg; });
    $$('[data-live],[data-status]').forEach(function(el){ el.classList.toggle('is-open', open); });
    $$('tr[data-day="'+day+'"]').forEach(function(r){ r.classList.add('today'); });
  }catch(e){}

  $$('[data-year]').forEach(function(el){ el.textContent = new Date().getFullYear(); });
})();
