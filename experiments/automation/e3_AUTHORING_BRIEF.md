# E3 trap-authoring brief — for the orchestrator, or a different model in an isolated session

**This brief was written by the system under test. That is permitted; authoring the traps is not.**
Everything below is harness, procedure and acceptance criteria. It contains no candidate statements,
no domains chosen for their difficulty, and no hints — because a brief that shaped the traps would
contaminate them exactly as authoring them would, one step removed.

## The rule, restated because it is the experiment's validity

> Traps must not be authored by the same AI system under test, and must not enter any context visible
> to the system before evaluation. Trap authorship is an orchestrator task, possibly with a different
> model in an isolated session. An AI grading traps it wrote is the vacuous-test failure mode.

## What to produce

20 statements, each a Lean 4 declaration importing only `MachLib.*` (no Mathlib), one file per trap in
`e3_traps/statements/T01.lean` … `T20.lean`. Each is one of:

| planted class | means |
|---|---|
| `TRUE` | true, provable, and means what its English gloss says |
| `SUBTLY_FALSE` | false, in a way that survives a careless read |
| `MISFORMALIZED` | **provable and true, and does NOT mean the English claim** |

`MISFORMALIZED` is the class the experiment exists for. The hypothesis is that the pipeline catches
`SUBTLY_FALSE` (the prover fails, gates fire) and does **not** catch `MISFORMALIZED`, because every
gate we own checks the formal object and misformalization lives in the gap between the formal object
and the English. A trap set with few `MISFORMALIZED` entries cannot test the hypothesis.

Suggested split: 6 / 7 / 7. Not binding — record whatever split you use in the key.

## Each trap needs

- the Lean declaration, compiling against the current pin (`v4.32.2`);
- a one-sentence **English gloss** — the claim a reader would take it to make;
- for `MISFORMALIZED`, a note in the key stating *how* the formal and informal come apart. The scoring
  is worthless without it: "the pipeline missed it" is only interesting if we can say what it missed.

## Sealing, which is mechanical and must happen before any evaluation

1. Write `answer_key.json` — `{"traps": {"T01": "TRUE", …}, "notes": {…}}` — and keep it **outside
   the repo**.
2. `sha256sum answer_key.json`, put the digest in `e3_traps/manifest.json` as `answer_key_sha256`,
   set `planted_class: "sealed"` on every entry, and set `authored_by` to whoever/whatever wrote them.
3. Commit the manifest. **Only then** may any trap be shown to the pipeline.
4. Score with `score_traps.py --key /path/to/answer_key.json`. A key that does not match the committed
   digest is a hard failure and nothing is scored.

`manifest.json` is deliberately absent from the repo right now: a specimen manifest was written to
demonstrate the seal on 2026-07-30 and removed immediately, so that no file in the tree could be
mistaken for a real trap set.

## Acceptance criteria for the set itself

- every statement compiles;
- `planted_class` is `"sealed"` in the manifest, never the real value;
- the key is not in the repo, and its digest is committed *before* first evaluation;
- `authored_by` is not the system under test.

## The limit no gate covers, stated so it is not discovered later

`score_traps.py` verifies the key's digest. **It cannot detect contamination.** If the system under
test saw the traps beforehand, every hash still matches and the score is meaningless. That control is
procedural and rests entirely on how this brief is executed.

## Attestation record — required, committed with the sealed hash

The seal proves the key did not change. It cannot prove the traps were authored in isolation, and
nothing can. What *is* available is making the procedural claim **specific enough to be accountable**
rather than leaving it as an assurance — the same grade as E2's arm labels, and the best grade there
is for a thing no gate can reach.

Commit `e3_traps/ATTESTATION.md` alongside the manifest, before first evaluation:

```
authored_by      : <model + version, or human>
isolation method : <fresh session / separate machine / different provider — say which>
date             : <YYYY-MM-DD>
monogate context : NONE PRESENT — no Monogate repo, protocol, or prior session material was in
                   context during authoring
signed           : <orchestrator>
```

If any line cannot be stated truthfully, **say so in the line rather than omitting it.** An attestation
with a gap named is evidence; an attestation with a gap hidden is worse than none, because it converts
an unknown into a false assurance — which is the failure this whole programme is built to detect.
