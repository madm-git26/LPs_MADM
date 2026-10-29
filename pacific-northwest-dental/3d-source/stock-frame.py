"""Re-frame the stock-style renders: crop to the content (incl. its soft shadow), centre it on white at 4:3
with an even margin, save 1200x900 WebP. python3 stock-frame.py <in-dir> <out-dir>"""
import sys
import numpy as np
from PIL import Image

NAMES = {'allon4': 'opt-all-on-4', 'snap2': 'opt-snap-in-2', 'snap4': 'opt-snap-in-4', 'bridge': 'opt-bridge', 'single': 'opt-single'}
src, dst = sys.argv[1], sys.argv[2]
for k, name in NAMES.items():
    im = Image.open(f'{src}/{k}.png').convert('RGB')
    a = np.asarray(im).astype(int)
    ys, xs = np.where(a.min(axis=2) < 246)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    w, h = x1 - x0, y1 - y0
    m = 0.07                                   # margin around the content
    W = max(w * (1 + 2 * m), h * (1 + 2 * m) * 4 / 3); H = W * 3 / 4
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    canvas = Image.new('RGB', (round(W), round(H)), (255, 255, 255))
    canvas.paste(im, (round(W / 2 - cx), round(H / 2 - cy)))
    canvas.resize((1200, 900), Image.LANCZOS).save(f'{dst}/{name}.webp', quality=84, method=6)
    print(name, 'content', (int(w), int(h)), '->', canvas.size)
