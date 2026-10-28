"""Build dental-implants-standalone.html: the landing page with every local asset embedded,
so it can be pasted into a page builder as a single file. Run: python3 build_standalone.py"""
import base64, json, re
from pathlib import Path

HERE = Path(__file__).parent
SRC, OUT = HERE / 'dental-implants.html', HERE / 'dental-implants-standalone.html'
MIME = {'.jpg': 'image/jpeg', '.webp': 'image/webp', '.mp4': 'video/mp4', '.webm': 'video/webm'}


def data_uri(rel):
    p = HERE / rel
    return f"data:{MIME[p.suffix]};base64,{base64.b64encode(p.read_bytes()).decode()}"


html = SRC.read_text()
# one video format is enough for every current browser; drop WebM to halve the payload
html = re.sub(r'\s*data-(desktop|mobile)-webm="[^"]+"', '', html)
html = re.sub(r'<link rel="preload" as="image"[^>]*>\n', '', html)
html = re.sub(r'<meta property="og:image"[^>]*>\n', '', html)
# every remaining local asset reference becomes a data URI
html = re.sub(r'(?<=")(assets/(?:video|img)/[^"{}?]+\.(?:jpg|webp|mp4))(?:\?v=\d+)?(?=")', lambda m: data_uri(m.group(1)), html)
# scroll-assembly frames
frames = [data_uri(f'assets/img/3d/seq/{i:03d}.webp') for i in range(40)]
html = html.replace('path:"assets/img/3d/seq/{i}.webp"', 'frames:' + json.dumps(frames), 1)
proc = [data_uri(f'assets/img/3d/proc/{i:03d}.webp') for i in range(48)]
html = html.replace('path:"assets/img/3d/proc/{i}.webp"', 'frames:' + json.dumps(proc), 1)
assert 'assets/' not in html.replace('wp-content/uploads', ''), 'unembedded local asset left'
OUT.write_text(html)
print(f'{OUT.name}: {OUT.stat().st_size / 1e6:.1f} MB')
