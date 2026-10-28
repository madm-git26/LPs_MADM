// node hero3d-render.js out.png [w] [h] ['{"az":0.3}']
const { chromium } = require('playwright'); const fs = require('fs');
(async () => {
  const [out, w = 1400, h = 1500, st = '{}'] = process.argv.slice(2);
  const br = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await br.newPage({ viewport: { width: +w, height: +h } });
  p.on('pageerror', e => console.log('pageerror', e.message));
  p.on('console', m => { if (m.type() === 'error') console.log('console', m.text()); });
  await p.goto(`http://127.0.0.1:8765/hero3d.html?w=${w}&h=${h}`); await p.waitForFunction('window.ready', null, { timeout: 120000 });
  const u = await p.evaluate(s => { window.renderState(s); return window.grab('image/png'); }, JSON.parse(st));
  fs.writeFileSync(out, Buffer.from(u.split(',')[1], 'base64'));
  await br.close(); console.log('wrote', out);
})();
