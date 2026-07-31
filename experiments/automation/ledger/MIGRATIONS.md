# Ledger migrations — additions that could not be made in place

## AMENDMENT 3 (2026-07-31): `preventive` promoted from note convention to schema field

Its stated recurrence condition was met: two instances, so the field is earned rather than guessed.

**The two pre-field instances are recorded HERE, not by editing their entries.**

| session | ts | entry | why it is preventive |
|---|---|---|---|
| `2026-07-30-phase25` | 2026-07-30T~19:0x | `taste` / `ai` / `structural` — declined to begin phase 26 on a generic "proceed" | the exhausted budget stopped a session from starting |
| `2026-07-31-menu` | 2026-07-31T~0x | `taste` / `ai` / `structural` — declined to author E3 traps or classify the retrospective | the contamination rule stopped two acts from starting |

**Why not edit the entries.** The orchestrator's ratification called this "a schema addition, not a
retro-labelling of content, so append-only survives". The schema addition does survive it — but adding
a key to an existing entry object still mutates that object, and `check_ledger_append_only.py` compares
the stored prefix element-by-element and would (correctly) convict.

Rather than weaken the gate to permit "purely additive" mutations — a category that is easy to state
and hard to police, since an added key can change how the existing ones read — the fact is recorded
append-only-natively, here. The gate stays exactly as strict as it was, and nothing about the past
moved. **This is the same call as `unrecorded` actors and unmarked pre-convention catches: the past is
not relabelled, it is annotated from outside.**
