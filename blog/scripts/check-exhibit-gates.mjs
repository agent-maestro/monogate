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

chk('provenance carries commit, digest and both NOT PROVED boundaries',
  data.commit.length === 40 && data.digest.length === 64 &&
  Object.keys(data.notProved).length === 2);

chk('exhibit escapes the article measure',
  /body:has\(\.ex-page\) main\{max-width:1180px\}/.test(css));

chk('every generic config really has eight, the locus seven',
  cfgs.every((c) => (c.isLocus ? c.count === 7 : c.count === 8)),
  cfgs.map((c) => c.count).join(','));

console.log();
if (bad) { console.error(`EXHIBIT GATES FAIL — ${bad} gate(s)`); process.exit(1); }
console.log('EXHIBIT GATES PASS — 8/8');
