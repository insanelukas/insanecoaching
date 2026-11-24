// v16 walk-through with screenshots: node shot16.js FILE OUT LANG SEX AGE GOAL WHY [W H] ; media requests are answered with the placeholders in ph/
const { chromium } = require('playwright'); const fs = require('fs'); const path = require('path');
const [FILE, OUT, LG, SEX, AGE, GOAL, WHY, W, H] = process.argv.slice(2);
(async () => {
  const b = await chromium.launch(); fs.mkdirSync(OUT, { recursive: true });
  const ctx = await b.newContext({ viewport: { width: Number(W || 390), height: Number(H || 844) }, hasTouch: Number(W || 390) < 700, deviceScaleFactor: 1, timezoneId: 'Europe/Vilnius' });
  const p = await ctx.newPage(); const errs = []; p.on('pageerror', e => errs.push(String(e)));
  const ph = f => fs.readFileSync(path.join(__dirname, 'ph', f));
  if (!process.env.REAL) await p.route("https://d8j0ntlcm91z4.cloudfront.net/**", r => {
    const u = r.request().url(); const tall = /\/g\//.test(u) || /_tall/.test(u);
    if (/\.mp4/.test(u)) return r.fulfill({ status: 200, contentType: 'video/mp4', body: ph(tall ? 'tall.mp4' : 'wide.mp4') });
    return r.fulfill({ status: 200, contentType: 'image/webp', body: ph(tall ? 'tall.webp' : 'wide.webp') });
  });
  let n = 0; const snap = async (name) => { await p.screenshot({ path: path.join(OUT, String(++n).padStart(2, '0') + '-' + name + '.png') }); };
  const click = async (sel, wait) => { await p.click(sel); await p.waitForTimeout(wait || 450); };
  await p.goto('file://' + path.resolve(FILE) + '#' + LG, { waitUntil: 'domcontentloaded' }); await p.waitForTimeout(500);
  await p.evaluate(() => { try { localStorage.setItem('ic-consent', 'none'); } catch (e) {} });
  await p.reload({ waitUntil: 'domcontentloaded' }); await p.waitForTimeout(500);
  await click('#hero-cta', 400); await snap('s1');
  await click(`dialog [data-q="sex"][data-v="${SEX}"][data-age="${AGE}"]`, 900); await snap('s2');
  await click(`dialog .g-roster:not([hidden]) .g-slot[data-v="${GOAL}"]`, 900); await snap('s2-tap');
  await click('#g-go', 900); await snap('s3');
  await click(`dialog [data-q="why"][data-v="${WHY}"]`, 600); await snap('s4');
  await click('dialog [data-q="mirror"][data-v="better"]', 600); await snap('s5');
  await click('#q-next', 500); await snap('s6');
  await click('dialog [data-q="tried"][data-v="diets"]', 500); await snap('s7');
  await click('dialog [data-q="blocker"][data-v="work"]', 500); await snap('s8');
  await click('dialog [data-q="start"][data-v="week"]', 1300); await snap('s9');
  const info = await p.evaluate(() => { const v = document.getElementById('scene-vid'), g = document.getElementById('g-vid'); return { scene: { hidden: document.getElementById('scene').hidden, src: v.getAttribute('src'), poster: document.getElementById('scene-img').getAttribute('src'), paused: v.paused, t: v.currentTime, tall: document.getElementById('scene').classList.contains('tall'), why: document.getElementById('scene-why').innerText }, pbar: document.getElementById('pbar-img').getAttribute('src'), cal: document.getElementById('cal-link').href }; });
  await p.evaluate(() => { const d = document.getElementById('book'); d.scrollTop = d.scrollHeight; }); await p.waitForTimeout(300); await snap('s9-end');
  console.log(JSON.stringify({ info, errs }, null, 1));
  await b.close();
})();
