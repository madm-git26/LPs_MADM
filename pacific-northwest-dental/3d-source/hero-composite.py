"""Composite the 3D implant tiles onto black with a brand-blue glow and soft light particles.
python3 hero-composite.py <desk-tile.png> <mob-tile.png> <out-dir>"""
import sys, random
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops

BLUE, BLUE_L = (3, 151, 214), (47, 178, 236)


def bbox(im, thr=40):
    a = np.asarray(im.convert('L')) > thr
    ys, xs = np.where(a)
    return int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())


def glow(size, cx, cy, rx, ry, color, alpha, blur):
    # draw on a padded canvas so the blur has no hard edge where the ellipse leaves the frame
    pad = int(blur * 3)
    L = Image.new('L', (size[0] + 2 * pad, size[1] + 2 * pad), 0)
    ImageDraw.Draw(L).ellipse((cx - rx + pad, cy - ry + pad, cx + rx + pad, cy + ry + pad), fill=int(255 * alpha))
    L = L.filter(ImageFilter.GaussianBlur(blur)).crop((pad, pad, pad + size[0], pad + size[1]))
    return Image.merge('RGB', [L.point(lambda v, c=c: v * c // 255) for c in color])


def particles(size, cx, cy, spread, n, seed, scale=1.0):
    rnd = random.Random(seed)
    out = Image.new('RGB', size, 0)
    for i in range(n):
        x = int(rnd.gauss(cx, spread[0])); y = int(rnd.gauss(cy, spread[1]))
        big = rnd.random() < 0.18
        r = (rnd.uniform(14, 34) if big else rnd.uniform(1.6, 5.5)) * scale
        a = rnd.uniform(0.05, 0.12) if big else rnd.uniform(0.25, 0.75)
        col = BLUE_L if rnd.random() < 0.7 else (220, 240, 255)
        L = Image.new('L', size, 0)
        ImageDraw.Draw(L).ellipse((x - r, y - r, x + r, y + r), fill=int(255 * a))
        L = L.filter(ImageFilter.GaussianBlur(r * (0.5 if big else 0.6)))
        out = ImageChops.add(out, Image.merge('RGB', [L.point(lambda v, c=c: v * c // 255) for c in col]))
    return out


def compose(tile, size, cx, cy, target_h, seed, n, spread):
    bx = bbox(tile); tile_scale = target_h / (bx[3] - bx[1])
    t = tile.resize((round(tile.size[0] * tile_scale), round(tile.size[1] * tile_scale)), Image.LANCZOS)
    # feather the tile's border so the faint bloom haze it cuts through never shows as a step
    w, h0 = t.size; f = int(min(w, h0) * 0.05)
    ramp = lambda n: np.clip(np.minimum(np.arange(n), np.arange(n)[::-1]) / f, 0, 1)
    m = np.outer(ramp(h0), ramp(w))[..., None]
    t = Image.fromarray((np.asarray(t).astype(float) * m).astype(np.uint8))
    x0, y0, x1, y1 = bbox(t)
    tcx, tcy = (x0 + x1) / 2, (y0 + y1) / 2
    base = Image.new('RGB', size, 0)
    h = y1 - y0
    base = ImageChops.add(base, glow(size, cx, cy, h * 0.42, h * 0.62, BLUE, 0.34, h * 0.16))
    base = ImageChops.add(base, glow(size, cx, cy + h * 0.12, h * 0.22, h * 0.14, BLUE_L, 0.22, h * 0.07))
    base = ImageChops.add(base, particles(size, cx, cy, spread, n, seed, scale=size[1] / 1500))
    layer = Image.new('RGB', size, 0)
    layer.paste(t, (round(cx - tcx), round(cy - tcy)))
    return ImageChops.screen(base, layer)


desk, mob, out = Image.open(sys.argv[1]).convert('RGB'), Image.open(sys.argv[2]).convert('RGB'), sys.argv[3]
D = compose(desk, (2400, 1500), round(0.538 * 2400), 720, 900, 7, 70, (520, 420))
D.save(f'{out}/hero-photo.webp', quality=80, method=6)
M = compose(mob, (960, 842), 480, 430, 640, 11, 34, (300, 220))
M.save(f'{out}/hero-photo-mobile.webp', quality=82, method=6)
D.resize((1200, 750)).save(f'{out}/preview-desk.jpg', quality=85); M.save(f'{out}/preview-mob.jpg', quality=85)
print('ok')
