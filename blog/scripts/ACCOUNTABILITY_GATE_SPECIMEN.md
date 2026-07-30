# Firing specimen — `check_accountability.py`

A gate with no firing specimen is unvalidated. Its PASS and its FAIL are equally uninformative until
it has been *seen* to do both: **convict** a state that should fail, and **acquit** a state that
should pass. Both were run on 2026-07-30, in the same commit that introduced the gate.

## Direction 1 — CAN-CONVICT

Four defects planted in `src/data/accountability.json`, one per rule the gate claims to enforce, plus
one that exposed a hole in the gate itself:

| planted defect | rule under test | caught |
|---|---|---|
| `TODO:` placeholder added to a MET row's artifacts | a row containing `TODO:` cannot be graded MET | ✅ |
| `gap` nulled on a PARTIAL row | PARTIAL/NOT_YET must name a gap | ✅ |
| `last_verified` set to `2025-01-01` | no row older than 120 days | ✅ (575d) |
| dead link `https://monogate.org/this-page-does-not-exist-specimen` | every artifact URL resolves | ✅ *(after repair — see below)* |

```
FAIL  row disclose-tool-use: graded MET but contains an unresolved TODO: placeholder
FAIL  row attribution: PARTIAL must name a gap
FAIL  row humanity-authorship: last verified 575d ago (max 120)
FAIL  internal link has no page in dist/: /this-page-does-not-exist-specimen
FAIL  URLError  TODO: authorship statement URL
ACCOUNTABILITY GATE: FAIL — 5 problem(s).     exit 1
```

### The specimen found a hole in the gate, which is the point of running one

On the first firing, the deliberately dead `monogate.org` link **passed**. The gate classified
same-site URLs as "internal — served by this build" and never checked them. That would have let a
typo'd link to the incident report ship silently, on a page whose entire thesis is that its links
resolve.

Repaired by resolving internal links against **`dist/`** rather than fetching them. That is also the
stronger check: HTTP-checking the live site cannot detect a page that was never built, because the
live site still serves the previous deploy. The gate now runs after `astro build` and fails if a
cited internal page is absent from the artifact about to ship — and fails, too, if `dist/` is missing
entirely, so "I forgot to build" can never read as "all links fine".

## Direction 2 — CAN-ACQUIT

Specimen removed, real data restored, site rebuilt:

```
1 SCHEMA        13 rows, 13 changelog entries
2 GRADE RIGOUR  (clean)
3 STALENESS     oldest row: 0d (limit 120d)
4 LINKS         4 internal links resolved against dist/
                16 external URLs checked
ACCOUNTABILITY GATE: PASS     exit 0
```

## What this gate does not do

It does not check that a grade is **correct** — no script can. It checks that the evidence a grade
points at is reachable, current, and non-placeholder, which is the part that rots silently while the
prose keeps reading as verified. The grades themselves are re-read by a human against their artifacts
at each quarterly re-verification (next: 2026-10-29).
