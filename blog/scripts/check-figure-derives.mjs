#!/usr/bin/env node
/**
 * VISUALIZED gate for /proofs/apollonius.
 *
 * The exhibit's claim is that the picture is a projection of the certificate, not an
 * illustration of it. Every other gate checks the JSON and the status logic; none of them
 * touch the drawing. So the one thing on the page backed only by "trust the author" was
 * the first thing a visitor looks at -- and a figure that silently drifted would still
 * build, still pass axe, and still look like a proof.
 *
 * This reads the RENDERED SVG and checks four things the code cannot assert about itself:
 *
 *   1. the affine map is recoverable from the three given circles alone, and every
 *      solution circle lands where the certificate's exact centre and radius say it must;
 *   2. each drawn solution circle is genuinely tangent to all three given circles, in
 *      screen space -- the picture depicts tangency rather than resembling it;
 *   3. the drawn tangency TYPE matches the row's mode label (o = external, i = internal),
 *      so identity preservation reaches the figure: the circle you see is the object the
 *      row names and the theorem certifies;
 *   4. perturbing a certificate coordinate MOVES the drawing. Checks 1-3 would all pass
 *      against a figure hardcoded to today's numbers; this is the one that cannot.
 *
 * Run: npm run check:figure     (needs playwright-core + a Firefox build)
 * Exit 2 means "could not check", which is not a pass.
 */
import { readFileSync, writeFileSync, mkdtempSync, cpSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import http from 'node:http';
import { existsSync, statSync, readdirSync } from 'node:fs';
import { extname } from 'node:path';

const bail = (m) => { console.error(`check-figure-derives: ${m}`); process.exit(2); };
let firefox;
try { ({ firefox } = await import('playwright-core')); }
catch { bail('playwright-core is not installed. `npm i -D playwright-core`.'); }

const cache = join(process.env.HOME || '', '.cache', 'ms-playwright');
const EXEC = process.env.FIREFOX_PATH || (existsSync(cache)
  ? readdirSync(cache).filter((d) => d.startsWith('firefox-'))
      .sort((a, b) => Number(b.split('-')[1]) - Number(a.split('-')[1]))
      .map((d) => join(cache, d, 'firefox', 'firefox')).find(existsSync)
  : null);
if (!EXEC) bail('no Firefox build in the Playwright cache. Set FIREFOX_PATH.');
if (!existsSync('dist/proofs/apollonius/index.html')) bail('no build — run `astro build` first.');

const TYPES = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css',
  '.json': 'application/json', '.svg': 'image/svg+xml', '.png': 'image/png', '.woff2': 'font/woff2' };
function serve(root) {
  const s = http.createServer((q, r) => {
    const u = decodeURIComponent((q.url || '/').split('?')[0]);
    for (const f of [join(root, u), join(root, u + '.html'), join(root, u, 'index.html')]) {
      if (existsSync(f) && statSync(f).isFile()) {
        r.writeHead(200, { 'content-type': TYPES[extname(f)] || 'application/octet-stream' });
        return r.end(readFileSync(f));
      }
    }
    r.writeHead(404); r.end('nf');
  });
  return new Promise((res) => s.listen(0, '127.0.0.1', () => res([s, s.address().port])));
}

let bad = 0, total = 0;
const chk = (name, cond, detail = '') => {
  total++;
  console.log(`  ${cond ? 'PASS' : 'FAIL'}  ${name}${detail ? '  ' + detail : ''}`);
  if (!cond) bad++;
};

const EV = (s) => {                       // exact strings -> float, sqrt-aware
  const t = String(s).replace(/sqrt\((\d+)\)/g, (_, n) => Math.sqrt(Number(n)).toString());
  if (!/^[-+*/(). \d]+$/.test(t)) throw new Error('unsafe expr: ' + s);
  return Function(`"use strict";return (${t})`)();
};

/** Read the figure for one configuration and return drawn geometry. */
async function readFigure(page, ci) {
  await page.evaluate((i) => document.querySelectorAll('.ex-tcard')[i].click(), ci);
  await page.waitForTimeout(300);
  return page.evaluate(() => ({
    circles: [...document.querySelectorAll('#fig circle')].map((c) => ({
      cx: +c.getAttribute('cx'), cy: +c.getAttribute('cy'), r: +c.getAttribute('r'),
      dashed: !!c.getAttribute('stroke-dasharray'),
    })),
    // Direct children only: the two axis rules live inside a <g>, the tangent line does not.
    lines: [...document.querySelectorAll('#fig > line')].map((l) => ({
      x1: +l.getAttribute('x1'), y1: +l.getAttribute('y1'),
      x2: +l.getAttribute('x2'), y2: +l.getAttribute('y2'),
    })),
    data: JSON.parse(document.getElementById('ex-data').textContent),
  }));
}

/** Recover the affine map from the three GIVEN circles only, then verify every solution. */
function audit(fig, cfg, label) {
  const d = EV(cfg.d), rho = EV(cfg.rho);
  const given = fig.circles.slice(0, 3), sols = fig.circles.slice(3);
  const k = (given[1].cx - given[0].cx) / d;              // px per unit
  const ox = given[0].cx, oy = given[0].cy;
  const okMap = Math.abs(given[2].cx - ox) < 0.5 && Math.abs(given[2].cy - (oy - k * d)) < 0.5
    && given.every((g) => Math.abs(g.r - k * rho) < 0.5);
  chk(`[${label}] the affine map is recoverable from the three given circles alone`, okMap,
    `${k.toFixed(3)} px/unit`);

  chk(`[${label}] one solution circle drawn per certified circle`, sols.length === cfg.sols.length,
    `${sols.length} drawn, ${cfg.sols.length} certified`);

  // 1. every drawn circle sits where the certificate's exact values say
  let placed = 0;
  const matched = new Map();
  for (const s of cfg.sols) {
    const px = ox + k * EV(s.xE), py = oy - k * EV(s.yE), pr = k * EV(s.rE);
    const hit = sols.findIndex((c, i) => !matched.has(i)
      && Math.abs(c.cx - px) < 0.6 && Math.abs(c.cy - py) < 0.6 && Math.abs(c.r - pr) < 0.6);
    if (hit >= 0) { matched.set(hit, s); placed++; }
  }
  chk(`[${label}] every drawn circle sits at its certificate centre and radius`,
    placed === cfg.sols.length, `${placed}/${cfg.sols.length} within 0.6px`);

  // 2 + 3. tangency, and the tangency TYPE the row's mode claims
  let tangent = 0, typed = 0;
  for (const [i, s] of matched) {
    const c = sols[i];
    const kinds = given.map((g) => {
      const dist = Math.hypot(c.cx - g.cx, c.cy - g.cy);
      if (Math.abs(dist - (c.r + g.r)) < 0.8) return 'o';       // external
      if (Math.abs(dist - Math.abs(c.r - g.r)) < 0.8) return 'i'; // internal
      return '?';
    });
    if (kinds.every((x) => x !== '?')) tangent++;
    if (kinds.join('') === s.mode.map((v) => (v > 0 ? 'o' : 'i')).join('')) typed++;
  }
  chk(`[${label}] every drawn circle is tangent to all three given circles, on screen`,
    tangent === cfg.sols.length, `${tangent}/${cfg.sols.length}`);
  chk(`[${label}] the drawn tangency type matches the mode the row claims`,
    typed === cfg.sols.length, `${typed}/${cfg.sols.length} (o = external, i = internal)`);
  // ── the eighth object ─────────────────────────────────────────────────────────
  // A line that merely looks tangent is the decoration this exhibit refuses. Held to the
  // same standard as the circles: it exists exactly where a class degenerates, it is drawn
  // from the certificate's own normal and offset, and it realises the (o,i,i) signature --
  // one given circle on one side, the other two on the other, all at distance rho.
  chk(`[${label}] a tangent line is drawn exactly where a class degenerates`,
    fig.lines.length === (cfg.line ? 1 : 0),
    `${fig.lines.length} drawn, ${cfg.line ? 1 : 0} certified`);

  if (cfg.line && fig.lines.length === 1) {
    const L = fig.lines[0];
    // unit normal of the DRAWN line, in screen space
    const ux = L.x2 - L.x1, uy = L.y2 - L.y1, len = Math.hypot(ux, uy);
    const Nx = -uy / len, Ny = ux / len;
    const sd = given.map((g) => (g.cx - L.x1) * Nx + (g.cy - L.y1) * Ny);
    chk(`[${label}] the drawn line is tangent to all three given circles`,
      sd.every((v) => Math.abs(Math.abs(v) - given[0].r) < 0.8),
      sd.map((v) => v.toFixed(2)).join(' / ') + ` vs r=${given[0].r.toFixed(2)}`);
    const signs = sd.map((v) => (v > 0 ? 1 : -1));
    chk(`[${label}] the drawn line separates them the way its mode claims`,
      signs[0] !== signs[1] && signs[1] === signs[2],
      `one side / other / other — mode ${cfg.line.mode.map((v) => (v > 0 ? 'o' : 'i')).join('')}`);
    // and it is the certificate's line, not merely a tangent line
    const want = { nx: cfg.line.nx_float, ny: cfg.line.ny_float, c: cfg.line.c_float };
    const inv = (sx, sy) => [(sx - ox) / k, (oy - sy) / k];      // screen -> math
    const [ax, ay] = inv(L.x1, L.y1), [bx, by] = inv(L.x2, L.y2);
    const off = [[ax, ay], [bx, by]].map(([x, y]) => want.nx * x + want.ny * y - want.c);
    chk(`[${label}] both endpoints satisfy the certificate's own equation`,
      off.every((v) => Math.abs(v) < 0.02), off.map((v) => v.toFixed(4)).join(' , '));
  }
  return { k, ox, oy };
}

const [srv, port] = await serve('dist');
const browser = await firefox.launch({ executablePath: EXEC });
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
const errs = [];
page.on('pageerror', (e) => errs.push(String(e).slice(0, 120)));
await page.goto(`http://127.0.0.1:${port}/proofs/apollonius`, { waitUntil: 'load' });
await page.waitForTimeout(1200);

const first = await readFigure(page, 0);
const CFGS = first.data.configs;
for (let i = 0; i < CFGS.length; i++) {
  const fig = i === 0 ? first : await readFigure(page, i);
  audit(fig, CFGS[i], CFGS[i].isLocus ? 'locus' : `d=${CFGS[i].d}`);
}
chk('the figure renders with no console error', errs.length === 0, errs[0] || 'none');
await browser.close();
srv.close();

// 4. CONVICT SPECIMEN — move a certificate coordinate; the drawing must follow.
// Everything above passes against a figure hardcoded to today's numbers. This does not.
const tmp = mkdtempSync(join(tmpdir(), 'apo-'));
cpSync('dist', join(tmp, 'dist'), { recursive: true });
const f = join(tmp, 'dist', 'proofs', 'apollonius', 'index.html');
let html = readFileSync(f, 'utf8');
const raw = /id="ex-data"[^>]*>([\s\S]*?)<\/script>/.exec(html)[1];
const obj = JSON.parse(raw);
const victim = obj.configs[0].sols[0];
const NEWX = EV(victim.xE) + 0.37;
victim.xE = String(NEWX); victim.x = NEWX;
html = html.replace(raw, JSON.stringify(obj));
writeFileSync(f, html);

const [srv2, port2] = await serve(join(tmp, 'dist'));
const b2 = await firefox.launch({ executablePath: EXEC });
const p2 = await b2.newPage({ viewport: { width: 1440, height: 1000 } });
await p2.goto(`http://127.0.0.1:${port2}/proofs/apollonius`, { waitUntil: 'load' });
await p2.waitForTimeout(1200);
const moved = await readFigure(p2, 0);
const g = moved.circles.slice(0, 3), k2 = (g[1].cx - g[0].cx) / EV(obj.configs[0].d);
const want = g[0].cx + k2 * NEWX;
const found = moved.circles.slice(3).some((c) =>
  Math.abs(c.cx - want) < 0.8 && Math.abs(c.r - k2 * EV(victim.rE)) < 0.8);
chk('moving a certificate coordinate moves the drawing (not hardcoded)', found,
  `nudged x by 0.37 units, expected cx ${want.toFixed(2)}`);
await b2.close(); srv2.close();

console.log();
if (bad) { console.error(`FIGURE GATES FAIL — ${bad} of ${total}`); process.exit(1); }
console.log(`FIGURE GATES PASS — ${total}/${total}`);
