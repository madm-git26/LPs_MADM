const { chromium } = require('playwright'); const fs = require('fs');
const lerp = (a, b, t) => a + (b - a) * t;
const cam = { az: -0.32, el: 0.22, dist: 76, ty: -3.6 };
const jobs = [
  ['render.html', 'w=1200&h=900&mode=still', [
    ['stills/step-1-scan.png', { ...cam, implantOn: 0, abutOn: 0, crownOn: 0, scan: 0.75, scanY: -5.5, ghost: 2.2 }],
    ['stills/step-2-implant.png', { ...cam, abutOn: 0, crownOn: 0 }],
    ['stills/step-3-heal.png', { ...cam, abutOn: 0, crownOn: 0, glow: 1 }],
    ['stills/step-4-abutment.png', { ...cam, crownOn: 0 }],
    ['stills/step-5-crown.png', { ...cam, ring: 0.45, ringScale: 1.15 }],
    ['stills/opt-single.png', { az: 0.36, el: 0.24, dist: 76, ty: -2.8, crownDrop: 6.5 }],
  ]],
  ['render.html', 'w=1200&h=900&mode=still&neighbors=0&layout=bridge', [
    ['stills/opt-bridge.png', { az: 0.38, el: 0.26, dist: 76, ty: -3.0, crownDrop: 5 }],
  ]],
  ['arch.html', 'w=1200&h=900&kind=allon4', [['stills/opt-all-on-4.png', {}]]],
  ['arch.html', 'w=1200&h=900&kind=snap2', [['stills/opt-snap-in-2.png', {}]]],
  ['arch.html', 'w=1200&h=900&kind=snap4', [['stills/opt-snap-in-4.png', {}]]],
];
const N = 40, seqStates = [];
for (let i = 0; i < N; i++) {
  const e = 1 - i / (N - 1), k = e * e * (3 - 2 * e);
  seqStates.push([`seq/${String(i).padStart(3, '0')}.png`, { jaw: 0, neighborsOn: 0, abutDrop: 7.5 * k, crownDrop: 16 * k, spin: -2.2 * k, ty: lerp(-3.0, 4.2, k), dist: lerp(57, 80, k), az: 0.32, el: 0.2 }, true]);
}
jobs.push(['render.html', 'w=900&h=900&mode=still&neighbors=0', seqStates]);
(async () => {
  const br = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const anchors = [];
  for (const [page, q, list] of (process.argv[2] === 'seq' ? jobs.slice(-1) : jobs)) {
    const qs = new URLSearchParams(q);
    const p = await br.newPage({ viewport: { width: +qs.get('w'), height: +qs.get('h') } });
    p.on('pageerror', e => console.log('pageerror', e.message));
    await p.goto(`http://127.0.0.1:8765/${page}?${q}`); await p.waitForFunction('window.ready', null, { timeout: 60000 });
    for (const [out, st, anc] of list) {
      const r = await p.evaluate(([s, a]) => { window.renderState(s); return { u: window.grab('image/png'), a: a ? window.anchors() : null }; }, [st, !!anc]);
      fs.writeFileSync(out, Buffer.from(r.u.split(',')[1], 'base64'));
      if (r.a) anchors.push(r.a);
    }
    await p.close(); console.log('done', page, q);
  }
  fs.writeFileSync('seq/anchors.json', JSON.stringify(anchors));
  await br.close();
})();
