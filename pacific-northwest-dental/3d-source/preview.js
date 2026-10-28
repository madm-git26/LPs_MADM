// usage: node preview.js "<query>" out.png t1 [extraJSON]   -> hero frame(s) at times
//        node preview.js "<query>" out.png state '<json>'    -> still
const { chromium } = require('playwright');
const fs = require('fs');
(async () => {
  const [query, out, a, b] = process.argv.slice(2);
  const qs = new URLSearchParams(query);
  const W = +qs.get('w') || 1920, H = +qs.get('h') || 1080;
  const br = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await br.newPage({ viewport: { width: W, height: H } });
  p.on('pageerror', e => console.log('pageerror', e.message));
  p.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') console.log(m.type(), m.text().slice(0, 300)); });
  await p.goto('http://127.0.0.1:8765/' + (qs.get('page') || 'render.html') + '?' + query);
  await p.waitForFunction('window.ready', null, { timeout: 60000 });
  let url;
  if (a === 'state') {
    await p.evaluate(s => window.renderState(JSON.parse(s)), b || '{}');
    url = await p.evaluate(() => window.grab('image/png'));
  } else {
    const times = a.split(',').map(Number);
    for (let i = 0; i < times.length; i++) {
      await p.evaluate(([t, e]) => window.renderAt(t, e ? JSON.parse(e) : null), [times[i], b || null]);
      const u = await p.evaluate(() => window.grab('image/jpeg', 0.9));
      const f = times.length > 1 ? out.replace(/(\.\w+)$/, `-${times[i]}$1`) : out;
      fs.writeFileSync(f, Buffer.from(u.split(',')[1], 'base64'));
    }
    await br.close(); return;
  }
  fs.writeFileSync(out, Buffer.from(url.split(',')[1], 'base64'));
  await br.close();
})();
