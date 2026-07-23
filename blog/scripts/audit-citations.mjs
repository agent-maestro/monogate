#!/usr/bin/env node
// scripts/audit-citations.mjs
//
// The cross-repo / staleness check theorems.astro's and atlas.astro's own
// build-time checks CAN'T do, because it reads a sibling repo (monogate-lean)
// that isn't part of this Astro build. Run before any deploy or release tag:
//
//   node scripts/audit-citations.mjs
//
// Checks:
//   1. Every theorems.json `deps`/`resolvedBy` id resolves (mirrors the
//      build-time check in theorems.astro — re-checked here so a green
//      `npm run build` isn't the only place this is enforced).
//   2. Every theorems.json `lean` citation's file exists in monogate-lean and
//      actually declares a theorem/lemma with the cited name(s).
//   3. Every atlas.json `proof`/note reference that looks like a catalog id
//      resolves to a real theorems.json entry, or is in the documented
//      external-reference allowlist below.
//   4. superbest.json/atlas.json superbestDisplay: every op_key either has a
//      canonical match in superbest.json's table or an explicit
//      nodes_override — this is also checked at build time in atlas.astro;
//      re-checked here for the same "don't rely on one enforcement point"
//      reason as #1.
//   5. pfaffian-towers.json: per-tower `count` sums to `function_total`.
//
// Exit code 0 = clean, 1 = at least one finding (ERROR). WARNINGs don't fail
// the exit code — they're things worth a human look, not a build-blocker.

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
const LEAN_REPO = process.env.MONOGATE_LEAN_PATH || path.resolve(ROOT, '../../monogate-lean');

const errors = [];
const warnings = [];

function readJSON(relPath) {
  return JSON.parse(fs.readFileSync(path.join(ROOT, relPath), 'utf8'));
}

const theorems = readJSON('src/data/theorems.json').results;
const atlas = readJSON('src/data/atlas.json');
const towers = readJSON('src/data/pfaffian-towers.json');
const superbest = readJSON('src/data/superbest.json');

const knownIds = new Set(theorems.map(t => t.id));

// Documented external references: legitimate, but intentionally not a
// /theorems catalog entry. Add here with a one-line reason, same discipline
// as machlib's AxiomLedger.lean legacyAxiomCallSiteAllowlist.
const EXTERNAL_REF_ALLOWLIST = {
  'R16-C1': 'Pre-catalog research-round reference (recip 1-node correction); not a /theorems entry.',
  'C-198': 'Pre-catalog research-round reference (Pfaffian tower independence search); not a /theorems entry.',
  'CAL-4': 'Pre-catalog research-round reference (calculus-costs session); not a /theorems entry.',
  'Q-1': 'Pre-catalog research-round reference (quantum-costs session); not a /theorems entry.',
  'Q-3': 'Pre-catalog research-round reference (quantum-costs session); not a /theorems entry.',
};

function leadingId(raw) {
  const m = raw.trim().match(/^[A-Za-z0-9_-]+/);
  return m ? m[0] : '';
}

// ─── 1. theorems.json internal dep/resolvedBy integrity ───
for (const r of theorems) {
  const refs = [r.deps, r.resolvedBy].filter(Boolean).join(',');
  for (const raw of refs.split(',')) {
    const id = leadingId(raw);
    if (id && !knownIds.has(id) && !(id in EXTERNAL_REF_ALLOWLIST)) {
      errors.push(`theorems.json: ${r.id} references unknown id "${id}" (deps/resolvedBy)`);
    }
  }
}

// ─── 2. Lean file/theorem existence ───
if (!fs.existsSync(LEAN_REPO)) {
  warnings.push(`monogate-lean not found at ${LEAN_REPO} (set MONOGATE_LEAN_PATH env var to override) — skipping Lean existence checks.`);
} else {
  for (const r of theorems) {
    if (!r.lean) continue;
    const filePath = path.join(LEAN_REPO, 'MonogateEML', r.lean.file);
    if (!fs.existsSync(filePath)) {
      errors.push(`theorems.json: ${r.id} cites Lean file "${r.lean.file}" — not found at ${filePath}`);
      continue;
    }
    const src = fs.readFileSync(filePath, 'utf8');
    const names = r.lean.theorem
      .split(/\/|\+/)
      .map(s => s.replace(/[()]/g, '').replace(/^\s*F1[3-6]\w*\s*/, '').trim())
      .filter(Boolean)
      .filter(s => /^[A-Za-z_][A-Za-z0-9_']*$/.test(s)); // skip prose fragments, keep identifier-shaped tokens
    for (const name of names) {
      const re = new RegExp(`\\b(theorem|lemma)\\s+${name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\b`);
      if (!re.test(src)) {
        errors.push(`theorems.json: ${r.id} cites "${name}" in ${r.lean.file} — no theorem/lemma with that name found`);
      }
    }
  }
}

// ─── 3. atlas.json proof/note references ───
function looksLikeCatalogId(token) {
  // Catalog ids: T\d+[a-z]*, ADD-T\d, P-\w+, O-\w+, C\d+, QCC, CHA,
  // T_[A-Z_]+. Deliberately conservative — only flag things that would
  // plausibly be typed expecting a /theorems entry to exist.
  return /^(T\d+[a-z]?|ADD-T\d+|P-[A-Z]+|O-[A-Z]+|C\d+|QCC|CHA|T_[A-Z_]+)$/.test(token);
}

// (?<!-) so a token like "C1" isn't matched as a standalone id when it's
// actually the tail of an already-allowlisted hyphenated compound like
// "R16-C1" (found by hand once already — see the same fix in the theorems.astro
// build-time check, which uses a leading-token match and doesn't have this
// problem, but this whole-string scanner needs it explicitly).
const CATALOG_ID_TOKEN = /(?<!-)\b(T\d+[a-z]?|ADD-T\d+|P-[A-Z]+|O-[A-Z]+|C\d+|QCC|CHA|T_[A-Z_]+)\b/g;

function checkProofField(context, value) {
  if (!value) return;
  // Scan the WHOLE string for catalog-id-shaped tokens, not just a leading
  // comma-split one — "1 LEAd node. T19." has its reference mid-sentence,
  // which a leading-token-only check misses (found by hand once already).
  for (const m of String(value).matchAll(CATALOG_ID_TOKEN)) {
    const id = m[0];
    if (!looksLikeCatalogId(id)) continue;
    if (knownIds.has(id) || id in EXTERNAL_REF_ALLOWLIST) continue;
    warnings.push(`atlas.json: ${context} references "${id}" — looks like a catalog id but isn't in theorems.json or the allowlist.`);
  }
}

for (const s of atlas.strata) {
  for (const e of s.entries) checkProofField(`strata[${s.depth}].${e.name}`, e.proof);
}
for (const r of atlas.specialFunctions) checkProofField(`specialFunctions.${r.fn}`, r.note);
for (const r of atlas.calculusCosts) checkProofField(`calculusCosts.${r.op}`, r.note);
for (const r of atlas.keyCostFacts) checkProofField(`keyCostFacts.${r.thm}`, r.thm);
for (const row of atlas.superbestDisplay) checkProofField(`superbestDisplay.${row.op_key}`, row.note);

// ─── 4. superbestDisplay <-> superbest.json join ───
const superbestKeys = new Set(
  superbest.table.map(row => (row.op.match(/^[a-zA-Z]+/) || [''])[0]).filter(Boolean)
);
for (const row of atlas.superbestDisplay) {
  if (!superbestKeys.has(row.op_key) && row.nodes_override === undefined) {
    errors.push(`atlas.json: superbestDisplay op_key "${row.op_key}" has no match in superbest.json's table and no nodes_override.`);
  }
}

// ─── 5. pfaffian-towers.json internal consistency ───
const towerSum = towers.towers.reduce((s, t) => s + t.count, 0);
if (towerSum !== towers.function_total) {
  errors.push(`pfaffian-towers.json: per-tower counts sum to ${towerSum} but function_total says ${towers.function_total}.`);
}

// ─── Report ───
console.log(`audit-citations: ${theorems.length} theorems, ${towers.towers.length} towers, ${atlas.superbestDisplay.length} superbest rows checked.`);
if (warnings.length) {
  console.log(`\n${warnings.length} warning(s):`);
  for (const w of warnings) console.log(`  - ${w}`);
}
if (errors.length) {
  console.log(`\n${errors.length} ERROR(s):`);
  for (const e of errors) console.log(`  - ${e}`);
  console.log('\nFAIL');
  process.exit(1);
} else {
  console.log('\nPASS (0 errors)');
}
