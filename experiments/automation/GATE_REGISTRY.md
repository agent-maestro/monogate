# Gate registry — experiments/automation

> **A gate with no firing specimen is UNVALIDATED, not passing.**

Doctrine and format inherited from `monogate-research/electronics_intake/tools/GATE_REGISTRY.md`, which
records the three incidents that produced the rule. That registry is scoped to the electronics-lab
domain and lives in a different repository, so these gates are registered here, beside the code they
guard. **`TODO: orchestrator` — decide whether the two registries consolidate.** A project with two
registries has the same problem as a project with none, one indirection later.

Specimens: `SPECIMENS.md`. A blank in *specimen* is queue, not comfort.

| gate | guards | specimen (convict) | specimen (acquit) | structurally blind to |
|---|---|---|---|---|
| `check_ledger_append_only.py` | E1 ledger integrity: schema, append-only vs git HEAD, SUSPECT flag | ✅ mutation + deletion, this commit (the specimen caught a path-resolution bug that made the gate pass a mutated ledger) | ✅ fixture restored, this commit | **a session that was never logged at all**; whether a `kind` was classified honestly |
| `check_e2_schedule_frozen.py` | E2 arm assignment cannot change after the first E2 session | ⬜ **both convict branches UNVALIDATED** — require an E2 session, which requires the prediction slots filled first | ✅ pre-registration phase, this commit | whether a session labelled `E2-ai` really had its target chosen by the AI |
| `score_traps.py` (seal) | E3 answer key matches the hash committed before evaluation | ✅ tampered key → HARD FAILURE, this commit | ✅ sealed key → SEAL INTACT, this commit | trap **difficulty**; **contamination** — a hash match does not mean the system had not already seen the traps |

## Notes on the blindness column

The blindness column is not a disclaimer; it is the part of the registry that gets used. Each entry
names a defect the gate would pass in silence:

- **E1** — the ledger's principal bias risk is absence, and absence is precisely what an append-only
  check cannot see. The `SUSPECT` flag catches "logged the win, skipped the work" and is blind to
  "skipped the session". E1's numbers should be read with that asymmetry in mind, not despite it.
- **E2** — the freeze gate compares a file to a hash. Whether the arm was *honoured* is an honesty
  requirement on the operator, stated as one in PROTOCOL.md rather than pretended into a gate.
- **E3** — the seal makes key-tampering detectable and does nothing about contamination. If the system
  under test saw the traps beforehand, every hash still matches and the score is still meaningless.
  Contamination control is procedural and cannot be mechanised by anything in this directory.
