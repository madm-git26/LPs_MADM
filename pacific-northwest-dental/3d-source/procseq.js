// Renders the scroll sequence for "The implant process in 3D": node procseq.js [N] [W] [H]
const { chromium } = require('playwright'); const fs = require('fs');
const N = +(process.argv[2] || 48), W = +(process.argv[3] || 1024), H = +(process.argv[4] || 768);
const clamp = (v, a, b) => Math.min(b, Math.max(a, v)), lerp = (a, b, t) => a + (b - a) * t;
const easeOut = t => 1 - Math.pow(1 - clamp(t, 0, 1), 3);
const easeInOut = t => { t = clamp(t, 0, 1); return t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };
// five equal stages: plan (scan + guide) / place / heal / abutment / crown
function procState(p) {
  const seg = (a, b) => clamp((p - a) / (b - a), 0, 1);
  const s = { time: p * 12, az: lerp(-0.42, 0.32, easeInOut(p)), el: lerp(0.2, 0.27, p), dist: 63, ty: -2.6 };
  const q1 = seg(0.02, 0.16); s.scanY = lerp(8, -14, easeInOut(q1)); s.scan = Math.sin(Math.PI * q1) * 0.85;
  s.ghost = seg(0.11, 0.18) * (1 - seg(0.3, 0.38));
  s.implantOn = p >= 0.2 ? 1 : 0; s.implantDrop = lerp(16, 0, easeOut(seg(0.21, 0.38)));
  s.glow = seg(0.42, 0.52) * (1 - seg(0.62, 0.7));
  s.abutOn = p >= 0.6 ? 1 : 0; s.abutDrop = lerp(13, 0, easeOut(seg(0.61, 0.77)));
  s.crownOn = p >= 0.8 ? 1 : 0; s.crownDrop = lerp(14, 0, easeOut(seg(0.81, 0.95)));
  return s;
}
(async () => {
  const br = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const pg = await br.newPage({ viewport: { width: W, height: H } });
  pg.on('pageerror', e => console.log('pageerror', e.message));
  await pg.goto(`http://127.0.0.1:8765/render.html?w=${W}&h=${H}&mode=still`);
  await pg.waitForFunction('window.ready', null, { timeout: 60000 });
  for (let i = 0; i < N; i++) {
    const u = await pg.evaluate(st => { window.renderState(st); return window.grab('image/png'); }, procState(i / (N - 1)));
    fs.writeFileSync(`procseq/${String(i).padStart(3, '0')}.png`, Buffer.from(u.split(',')[1], 'base64'));
  }
  await br.close(); console.log('rendered', N);
})();
