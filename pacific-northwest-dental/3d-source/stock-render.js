// node stock-render.js <outdir> [w] [h] [kinds...]  — renders the stock-style pricing images to PNG
const { chromium } = require('playwright'); const fs = require('fs');
(async () => {
  const [out, w = 1600, h = 1200, ...kinds] = process.argv.slice(2);
  const list = kinds.length ? kinds : ['allon4', 'snap2', 'snap4', 'bridge', 'single'];
  const br = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  for (const k of list) {
    const p = await br.newPage({ viewport: { width: +w, height: +h } });
    p.on('pageerror', e => console.log('pageerror', e.message));
    await p.goto(`http://127.0.0.1:8765/stock.html?kind=${k}&w=${w}&h=${h}`); await p.waitForFunction('window.ready', null, { timeout: 120000 });
    const u = await p.evaluate(() => { window.renderState({}); return window.grab('image/png'); });
    fs.writeFileSync(`${out}/${k}.png`, Buffer.from(u.split(',')[1], 'base64')); console.log('wrote', k);
    await p.close();
  }
  await br.close();
})();
