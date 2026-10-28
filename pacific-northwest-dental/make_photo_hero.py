"""Build dental-implants-photo-hero.html from dental-implants.html: the same page, but the hero shows a
marketing photo (assets/img/hero/) instead of the 3D video. Re-run after editing the main page:
python3 make_photo_hero.py && python3 build_standalone.py"""
from pathlib import Path

HERE = Path(__file__).parent
SRC, OUT = HERE / 'dental-implants.html', HERE / 'dental-implants-photo-hero.html'

html = SRC.read_text()


def swap(old, new):
    global html
    assert html.count(old) == 1, f'expected exactly one match for: {old[:70]!r}'
    html = html.replace(old, new)


# preload the photo cut that fits the screen instead of the video posters
swap('''<link rel="preload" as="image" href="assets/video/hero-poster.jpg" media="(min-width: 900px)">
<link rel="preload" as="image" href="assets/video/hero-poster-mobile.jpg" media="(max-width: 899px)">''',
     '''<link rel="preload" as="image" href="assets/img/hero/hero-photo.webp" media="(min-width: 600px)" fetchpriority="high">
<link rel="preload" as="image" href="assets/img/hero/hero-photo-mobile.webp" media="(max-width: 599px)" fetchpriority="high">''')

# ---- CSS ----
swap('.hero-video{width:100%;height:100%;object-fit:cover;object-position:50% 32%}',
     '.hero-photo,.hero-photo img{display:block;width:100%;height:100%}\n'
     '.hero-photo img{object-fit:cover;object-position:50% 34%}\n'
     '.hero .lead,.hero-note{text-wrap:balance}')
start = html.index('.vid-ctl{position:absolute')
end = html.index('/* phones: headline first')
html = html[:start] + html[end:]
swap('/* phones: headline first, then the 3D video, then the rest */',
     '/* phones: headline first, then the photo, then the rest */')

swap('''  /* desktop hero: 3D video full-bleed behind headline + form */''',
     '''  /* desktop hero: photo full-bleed behind headline + form; the subject sits in the gap between them */''')
swap('  .hero-video{object-position:56% 50%}', '  .hero-photo img{object-position:50% 46%}')
start = html.index('  .hero-shade{background:\n    linear-gradient(90deg,rgba(0,0,0,.95)')
end = html.index('\n', html.index('  .vid-ctl{right:auto'))
# 900-1199px: the copy column is pinned to the left edge (20-480px), so the shade is measured from there
html = html[:start] + '''  .hero-shade{background:
    linear-gradient(90deg,rgba(0,0,0,.94) 0,rgba(0,0,0,.88) 420px,rgba(0,0,0,.5) 490px,rgba(0,0,0,0) 560px,rgba(0,0,0,0) calc(100% - 420px),rgba(0,0,0,.3) calc(100% - 300px),rgba(0,0,0,.62) 100%),
    linear-gradient(180deg,rgba(0,0,0,.42) 0%,transparent 18%,transparent 76%,rgba(0,0,0,.9) 100%)}''' + html[end:]
swap('  .hero-grid{display:grid;grid-template-columns:minmax(0,540px) 1fr 430px;',
     '  .hero h1{font-size:clamp(2.9rem,4.4vw,3.6rem)}\n'
     '  .hero .btn-lg{padding-left:24px;padding-right:24px}\n'
     '  .hero .lead{max-width:440px}\n'
     '  .hero-grid{display:grid;grid-template-columns:minmax(0,460px) 1fr 400px;')
swap('''@media(min-width:1200px){
  .hero-grid{grid-template-columns:minmax(0,560px) 1fr 440px}
}''', '''@media(min-width:1200px){
  .hero-grid{grid-template-columns:minmax(0,520px) 1fr 410px}
  .hero .lead{max-width:460px}
  /* the content is centred, so the shade is pinned to the centre: dark behind the copy (centre-600..-80px), clear over the patient */
  .hero-shade{background:
    linear-gradient(90deg,rgba(0,0,0,.94) 0%,rgba(0,0,0,.88) calc(50% - 210px),rgba(0,0,0,.52) calc(50% - 100px),rgba(0,0,0,0) calc(50% - 10px),rgba(0,0,0,0) calc(50% + 200px),rgba(0,0,0,.3) calc(50% + 330px),rgba(0,0,0,.62) 100%),
    linear-gradient(180deg,rgba(0,0,0,.42) 0%,transparent 18%,transparent 76%,rgba(0,0,0,.9) 100%)}
}
@media(min-width:1500px){
  /* very wide screens: keep the photo at a sensible size and fade its edges into the black hero */
  .hero-photo{width:1500px;margin:0 auto;-webkit-mask-image:linear-gradient(90deg,transparent,#000 12%,#000 88%,transparent);mask-image:linear-gradient(90deg,transparent,#000 12%,#000 88%,transparent)}
}''')

# ---- markup ----
start = html.index('    <video class="hero-video"')
end = html.index('  <div class="wrap hero-grid">')
html = html[:start] + '''    <picture class="hero-photo">
      <source media="(max-width: 599px)" srcset="assets/img/hero/hero-photo-mobile.webp" width="960" height="842">
      <img src="assets/img/hero/hero-photo.webp" alt="Smiling senior man in a dark suit jacket with his arms crossed" width="2400" height="1847" fetchpriority="high">
    </picture>
    <div class="hero-shade" aria-hidden="true"></div>
  </div>
''' + html[end:]
swap('  <symbol id="i-pause" viewBox="0 0 24 24"><path d="M6 4h4v16H6zM14 4h4v16h-4z"/></symbol>\n', '')

# ---- script: the video player is gone ----
start = html.index('  /* hero 3D video:')
end = html.index('  /* price count-up */')
html = html[:start] + html[end:]

for gone in ('heroVideo', 'vidCtl', 'vid-ctl', 'hero-video', 'assets/video/'):
    assert gone not in html, f'{gone} still referenced'
OUT.write_text(html)
print(f'{OUT.name}: {len(html):,} bytes')
