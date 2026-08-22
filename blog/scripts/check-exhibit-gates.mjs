#!/usr/bin/env node
// Release gates for /proofs/apollonius. Run after `astro build`, before deploy.
//
// These check the CLAIM BOUNDARY, not the styling: an exhibit that quietly upgrades
// "computed" to "certified", or loses the exceptional-locus default, or starts drawing
// from transcribed coordinates, would still build and still look right.
import { readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';

const DIST = 'dist/proofs/apollonius/index.html';
const SRC = 'src/pages/proofs/apollonius.astro';
let bad = 0, total = 0;
const chk = (name, cond, detail = '') => {
  total++;
  console.log(`  ${cond ? 'PASS' : 'FAIL'}  ${name}${detail ? '  ' + detail : ''}`);
  if (!cond) bad++;
};

const html = readFileSync(DIST, 'utf8');
const src = readFileSync(SRC, 'utf8');
const css = [...html.matchAll(/_astro\/[^"]*\.css/g)]
  .map((m) => readFileSync(join('dist', m[0]), 'utf8')).join('\n');
const data = JSON.parse(/id="ex-data"[^>]*>([\s\S]*?)<\/script>/.exec(html)[1]);
const cfgs = data.configs, def = cfgs[data.defaultConfig];

chk('default view is the exceptional case', def.isLocus && def.count === 7,
  `count=${def.count} d=${def.d}`);

const sides = cfgs.filter((c) => !c.isLocus).map((c) => c.side).sort();
chk('neighbours lie on OPPOSITE sides of d^2 = 8rho^2',
  sides.length === 2 && sides[0] === 'above' && sides[1] === 'below', sides.join('/'));

chk('coordinates come from the artifact, none transcribed',
  src.includes('apollonius-evidence.json') && !/r_exact"\s*:\s*"/.test(src));

chk('solutions panel stays COMPUTED',
  html.includes('Exact computed solution') && !html.includes('Certified solution'));

const deg1 = def.modes.filter((m) => m.deg === 1);
chk('degree-drop rows: lead = 0, degree = 1, discriminant > 0',
  deg1.length === 2 && deg1.every((m) => m.lead === '0' && Number(m.disc) > 0),
  `${deg1.length} rows, disc=${deg1[0]?.disc}`);

// Bound to the boundary itself, not to how many boundaries there happen to be. The earlier
// form asserted `Object.keys(notProved).length === 2`, which is a snapshot: when the
// list-cardinality claim was proved on 2026-08-19 the correct count became 1, and a literal
// count would have had to be edited to keep the gate green -- training the next person to edit
// the guard instead of reading it.
chk('provenance carries commit and digest',
  data.commit.length === 40 && data.digest.length === 64);

// The coordinates disclaimer is the one that MUST survive: MachLib proves the count and its
// structure, not the particular numbers rendered on the page.
// Retiring the last disclaimer is only legitimate once every point is checked AND the retirement
// is recorded. An empty NOT PROVED with unchecked points would be the exact overclaim this whole
// exhibit exists to prevent.
{
  const all = data.configs.flatMap((c) => c.sols);
  const unchecked = all.filter((s) => !s.lean).length;
  chk('NOT PROVED is empty only when nothing is unchecked',
    unchecked > 0 ? Object.keys(data.notProved).length > 0 : true,
    `${unchecked} unchecked, ${Object.keys(data.notProved).length} disclaimer(s)`);
  chk('a fully-checked exhibit records the retirement',
    unchecked > 0 || Object.keys(data.corrected ?? {}).some((k) => /all 23/i.test(k)));
}

// Nothing may leave NOT PROVED silently. A claim that was once disclaimed and is now proved has
// to say so, with its reason, where a reader of the old page would look for it.
chk('retired disclaimers are recorded, not deleted',
  Object.entries(data.corrected ?? {}).every(([, v]) => /WAS listed NOT PROVED/i.test(v)));

// ...and RENDERED. Carrying a correction in the data blob while showing nothing is the same as
// deleting it, from the only perspective that matters: the reader's.
chk('retired disclaimers are rendered, not just carried',
  /id=.corrected./.test(html) && /D\.corrected/.test(html),
  Object.keys(data.corrected ?? {}).length + ' correction(s)');

// And the upgrade must be backed by a real declaration, not by prose.
chk('list-cardinality claim now cites a theorem',
  !Object.keys(data.notProved).some((k) => /cardinality/i.test(k)) &&
  Object.values(data.proved).some((v) => /eight_solutions$/.test(v)),
  Object.keys(data.corrected ?? {}).join(','));

// A point may claim PROVED only if the evidence names the theorem. This is the same rule as the
// depth-ladder's two-sided gate, one level down: a status without a citation is a status typed by a
// human, and those drift.
{
  const allSols = data.configs.flatMap((c) => c.sols);
  const checked = allSols.filter((s) => s.lean);
  chk('every Lean-checked point cites a theorem',
    checked.every((s) => /^MachLib\.[A-Za-z0-9_.]+$/.test(s.lean)),
    `${checked.length} of ${allSols.length} points checked`);
  chk('the renderer derives the point status from the citation, not a literal',
    /s\.lean \? 'PROVED/.test(src) && !/'Lean-checked point', 'PROVED'/.test(src));
  // And the disclaimer must still cover the ones that are NOT checked.
  chk('unchecked points are still disclaimed',
    checked.length < allSols.length
      ? Object.keys(data.notProved).some((k) => /coordinate/i.test(k))
      : true,
    `${allSols.length - checked.length} still computed-only`);
}

chk('exhibit escapes the article measure',
  /body:has\(\.ex-page\) main\{max-width:1180px\}/.test(css));

chk('every generic config really has eight, the locus seven',
  cfgs.every((c) => (c.isLocus ? c.count === 7 : c.count === 8)),
  cfgs.map((c) => c.count).join(','));

// ── IDENTITY PRESERVATION ────────────────────────────────────────────────────────
// Provenance correctness is not only "does every row cite a theorem". It is "does the
// displayed row identify the exact mathematical object that theorem certifies". Every
// gate above could pass while the UI attached the right citation to the wrong witness.
//
// The concrete failure that prompted these: `primary: m.mode[0] === 1` -- a property of
// the MODE -- was used to say which of a class's two CIRCLES a row was. Every circle
// appears in the certificate twice, positive under mode m and negative under -m, so its
// label is whichever of {m, -m} gives a positive radius. Both circles of one class can
// land on the same mode (d = 5/2: two circles under ioo, none under oii). The figure then
// drew two dashed circles and no solid one, falsifying its own caption -- with correct
// data, correct citations, and a clean build.
// These gates quote the defective code verbatim in their own comments, and the page does
// too. Match against source with comments stripped, or the documentation trips the gate
// that documents it -- which is how the first run of this block failed.
const code = src.replace(/\/\*[\s\S]*?\*\//g, '')
  .split('\n').filter((l) => !/^\s*(\/\/|\*)/.test(l)).join('\n');

const ev = JSON.parse(readFileSync('src/data/apollonius-evidence.json', 'utf8'));
const L = (m) => m.map((v) => (v > 0 ? 'o' : 'i')).join('');
const evCfgs = ev.COMPUTED.configurations;

chk('projection is faithful: displayed rows are exactly the certificate\'s positive roots',
  cfgs.every((c, i) => {
    const shown = c.sols.map((s) => [L(s.mode), s.xE, s.yE, s.rE].join('|')).sort();
    const cert = evCfgs[i].modes.flatMap((m) => m.roots.filter((r) => r.positive_radius)
      .map((r) => [L(m.mode), r.x_exact, r.y_exact, r.r_exact].join('|'))).sort();
    return JSON.stringify(shown) === JSON.stringify(cert);
  }), `${cfgs.reduce((n, c) => n + c.sols.length, 0)} rows`);

chk('antipodal law holds in the certificate: roots(-m) = -roots(m)',
  evCfgs.every((cfg) => {
    const by = new Map(cfg.modes.map((m) => [m.mode.join(','), m]));
    return cfg.modes.every((m) => {
      const c = by.get(m.mode.map((v) => -v).join(','));
      if (!c) return false;
      const a = m.roots.map((r) => r.r_float).sort((x, y) => x - y);
      const b = c.roots.map((r) => -r.r_float).sort((x, y) => x - y);
      return a.every((v, i) => Math.abs(v - b[i]) < 1e-9);
    });
  }));

chk('each displayed circle is positive under exactly one of {m, -m}, so its label is canonical',
  evCfgs.every((cfg) => {
    const by = new Map(cfg.modes.map((m) => [m.mode.join(','), m]));
    return cfg.modes.every((m) => {
      const c = by.get(m.mode.map((v) => -v).join(','));
      return m.roots.filter((r) => r.positive_radius).every((r) =>
        c.roots.some((q) => Math.abs(q.r_float + r.r_float) < 1e-9 && !q.positive_radius));
    });
  }));

chk('circles are distinct by centre AND radius — radius alone does not identify one',
  cfgs.every((c) => new Set(c.sols.map((s) => `${s.xE}|${s.yE}|${s.rE}`)).size === c.sols.length),
  cfgs.map((c) => `${new Set(c.sols.map((s) => s.rE)).size} radii for ${c.sols.length} circles`).join(', '));

// Written first as `A && B === false ? C : true`, which precedence made unfailable. A gate
// that cannot fail is worse than no gate: it reports PASS and buys nothing.
chk('the row shows the centre, so four equal radii are four visibly different circles',
  /class="ctr">c = \(/.test(code) && /\.ctr\s*\{/.test(css));

chk('row -> root -> theorem citation is one-to-one',
  cfgs.every((c) => {
    const cited = c.sols.filter((s) => s.lean).map((s) => s.lean);
    return new Set(cited).size === cited.length;
  }), `${cfgs.reduce((n, c) => n + c.sols.filter((s) => s.lean).length, 0)} citations, all distinct`);

chk('solid/dashed keys off the SOLUTION, not the mode — one first member per class',
  cfgs.every((c) => [0, 1, 2, 3].every((k) => {
    const mem = c.sols.filter((s) => s.cls === k).map((s) => s.member).sort();
    return mem.every((v, i) => v === i);
  })),
  cfgs.map((c) => [0, 1, 2, 3].map((k) => c.sols.filter((s) => s.cls === k).length).join('')).join(' '));

chk('the class-of-a-mode flag is never derived from the mode again',
  !/primary:\s*m\.mode\[0\]/.test(code) && !/s\.primary/.test(code));

chk('a class holding two circles on ONE mode still renders one solid and one dashed',
  cfgs.some((c) => [0, 1, 2, 3].some((k) => {
    const mem = c.sols.filter((s) => s.cls === k);
    return mem.length === 2 && L(mem[0].mode) === L(mem[1].mode);
  })) && cfgs.every((c) => [0, 1, 2, 3].every((k) => {
    const mem = c.sols.filter((s) => s.cls === k);
    return mem.filter((s) => s.member === 0).length === (mem.length ? 1 : 0);
  })), 'the d = 5/2 case that broke the caption');

chk('an antipodal class is rendered as a PAIR, never a lone representative',
  Array.isArray(data.classModes) && data.classModes.length === 4 &&
  data.classModes.every((pair) => pair.length === 2 &&
    pair[0].split('').every((ch, i) => ch !== pair[1][i])) &&
  !/const CN = \['\(o,o,o\)'/.test(src),
  data.classModes.map((p) => p.join('/')).join(' '));

chk('epistemic status on the banner is derived from the certificate, not typed',
  !/exact, not in Lean/.test(code) && !/'Lean gates', '8 \/ 8'/.test(code) &&
  cfgs.every((c) => c.leanChecked === c.sols.filter((s) => s.lean).length),
  cfgs.map((c) => `${c.leanChecked}/${c.count}`).join(' '));

chk('a fully checked config says so, instead of understating itself',
  cfgs.every((c) => c.leanChecked !== c.count || /LEAN-CHECKED/.test(html) || /LEAN-CHECKED/.test(src)));

// The status a claim carries must not outrun the toolchain that enforces it. VISUALIZED sat
// at "pending" while the figure was in fact unchecked -- honest. The failure mode now is the
// opposite: flipping it to GATED and then quietly dropping the gate from the release path.
// ── the count that does not drop ──────────────────────────────────────────────────
// 8 -> 7 -> 8 is the finite count. The exhibit now also states the compactified one, and a
// claim of "eight throughout" is only worth making if the eighth object is really there.
chk('the generalized count is eight in every configuration',
  cfgs.every((c) => c.countGeneralized === 8),
  cfgs.map((c) => `${c.count}${c.line ? '+line' : ''}`).join(' -> '));

chk('a tangent line exists exactly where a class degenerates, and nowhere else',
  evCfgs.every((cfg, i) => {
    const degenerate = cfg.modes.some((m) => m.degree === 1);
    return degenerate === !!cfg.tangent_line && degenerate === !!cfgs[i].line;
  }));

chk('the tangent line satisfies OIITangentLine exactly, all four conditions',
  evCfgs.every((cfg) => !cfg.tangent_line ||
    (cfg.tangent_line.exact &&
     Object.values(cfg.tangent_line.residuals).every((r) => r === '0'))),
  evCfgs.filter((c) => c.tangent_line).map((c) =>
    Object.keys(c.tangent_line.residuals).length + ' residuals zero').join('') || 'n/a');

chk('the line carries the degenerate class, not some other one',
  evCfgs.every((cfg) => !cfg.tangent_line ||
    cfg.tangent_line.degenerate_modes.every((m) =>
      cfg.modes.find((x) => x.mode.join() === m.join())?.degree === 1)));

chk('the packet attests a commit where every citation resolves',
  ev.ATTESTED.citations_resolve_at_commit === true,
  `${ev.ATTESTED.machlib_commit.slice(0, 12)} pinned=${ev.ATTESTED.commit_pinned}`);

// ── the sweep must not dilute the checked count ───────────────────────────────────
// 33 frames x 8 circles is 250-odd coordinates that nobody has stated in Lean. Folded into
// the same pool as the three configurations, "23 of 23 Lean-checked" quietly becomes "23 of
// 287" -- a hard-won claim destroyed by a feature, with no line of code looking wrong.
{
  const SW = ev.SWEPT || {};
  const frames = SW.frames || [];
  chk('the sweep exists and every frame is exact', frames.length > 0 &&
    frames.every((f) => f.all_tangencies_exact), `${frames.length} frames`);

  // The detail said "0 cited" as a typed literal, so the first specimen run printed
  // "263 frame coordinates, 0 cited" NEXT TO ITS OWN FAILURE. A gate that misreports what
  // it found is a gate people learn to skim. Derived now, like everything else here.
  const swCited = frames.reduce((n, f) => n + f.circles.filter((c) => c.lean !== null).length, 0);
  chk('NO sweep coordinate claims a Lean citation', swCited === 0,
    `${frames.reduce((n, f) => n + f.circles.length, 0)} frame coordinates, ${swCited} cited`);

  chk('the Lean-checked count still comes only from the three configurations',
    cfgs.reduce((n, c) => n + c.sols.filter((s) => s.lean).length, 0) === 23,
    `${cfgs.reduce((n, c) => n + c.sols.filter((s) => s.lean).length, 0)} of 23`);

  chk('the sweep carries its COMPUTED status in words, not just by omission',
    /COMPUTED/.test(SW.status || '') && /not.*Lean|no coordinate checked/i.test(SW.status || ''),
    SW.status || 'MISSING');

  chk('exactly one frame is the locus, and only it carries a line',
    frames.filter((f) => f.tangent_line).length === 1);

  chk('the generalized count is eight in every frame too',
    frames.every((f) => f.count_generalized === 8),
    `finite counts ${[...new Set(frames.map((f) => f.count))].sort().join('/')}`);

  // The sweep and the headline data must be the same mathematics, not two computations that
  // happen to look alike.
  const locusFrame = frames.find((f) => f.tangent_line);
  const locusCfg = evCfgs.find((c) => c.modes.some((m) => m.degree === 1));
  const near = (a, b) => Math.abs(a - b) < 1e-9;
  chk('the locus frame agrees with the certified locus configuration',
    !!locusFrame && !!locusCfg && (() => {
      const A = locusFrame.circles.map((c) => [c.x, c.y, c.r]).sort((p, q) => p[2] - q[2]);
      const B = locusCfg.modes.flatMap((m) => m.roots.filter((r) => r.positive_radius)
        .map((r) => [r.x_float, r.y_float, r.r_float])).sort((p, q) => p[2] - q[2]);
      return A.length === B.length && A.every((v, i) => v.every((x, j) => near(x, B[i][j])));
    })(), `${locusFrame?.circles.length} vs ${locusCfg ? locusCfg.count_positive_radius : '?'}`);

  chk('the sweep really crosses the locus, with the label flip on the far side',
    (() => {
      const li = frames.findIndex((f) => f.tangent_line);
      const lbl = (f) => f.degenerating_class.map((z) =>
        z.mode.map((v) => (v > 0 ? 'o' : 'i')).join(''));
      return li > 0 && li < frames.length - 1
        && lbl(frames[li - 1]).every((x) => x === 'ioo')
        && lbl(frames[li + 1]).includes('oii');
    })(), 'ioo,ioo below -> line -> ioo,oii above');
}

{
  const vis = ev.VISUALIZED || {};
  const pd = JSON.parse(readFileSync('package.json', 'utf8')).scripts.predeploy || '';
  chk('a non-pending VISUALIZED status is actually enforced by the release path',
    vis.status === 'pending' || /check:figure/.test(pd), `status=${vis.status}`);
}

console.log();
if (bad) { console.error(`EXHIBIT GATES FAIL — ${bad} of ${total} gate(s)`); process.exit(1); }
console.log(`EXHIBIT GATES PASS — ${total}/${total}`);
