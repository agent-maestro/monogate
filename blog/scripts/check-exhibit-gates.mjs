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
let bad = 0;
const chk = (name, cond, detail = '') => {
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
chk('coordinates outside the flagship are still declared NOT PROVED',
  Object.keys(data.notProved).some((k) => /coordinate/i.test(k)) &&
  /COMPUTED only/i.test(Object.values(data.notProved).join(' ')));

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

console.log();
if (bad) { console.error(`EXHIBIT GATES FAIL — ${bad} gate(s)`); process.exit(1); }
console.log('EXHIBIT GATES PASS — 15/15');
