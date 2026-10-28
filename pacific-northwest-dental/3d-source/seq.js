// node seq.js "<query>" outdir fps duration '<extraJSON>'
const { chromium } = require('playwright'); const fs = require('fs');
(async () => {
  const [query, dir, fps, dur, extra] = process.argv.slice(2);
  const qs = new URLSearchParams(query); const W = +qs.get('w'), H = +qs.get('h');
  fs.mkdirSync(dir, { recursive: true });
  const br = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await br.newPage({ viewport: { width: W, height: H } });
  p.on('pageerror', e => console.log('pageerror', e.message));
  await p.goto('http://127.0.0.1:8765/render.html?' + query);
  await p.waitForFunction('window.ready', null, { timeout: 60000 });
  const n = Math.round(+fps * +dur); const t0 = Date.now();
  for (let i = 0; i < n; i++) {
    const u = await p.evaluate(([t, e]) => { window.renderAt(t, e ? JSON.parse(e) : null); return window.grab('image/jpeg', 0.93); }, [i / +fps, extra || null]);
    fs.writeFileSync(`${dir}/f${String(i).padStart(4, '0')}.jpg`, Buffer.from(u.split(',')[1], 'base64'));
  }
  console.log('frames', n, 'sec', (Date.now() - t0) / 1000);
  await br.close();
})();
