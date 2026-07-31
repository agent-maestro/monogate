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


## 2026-07-31 — a `preventive` flag cannot be added retroactively

**Situation.** An entry in `2026-07-31-xplusone-depth2.json` recorded a catch that qualified under
AMENDMENT 3 (`preventive`: the catch stopped an act before it executed) but was logged without the
flag. The obvious fix — set `preventive: true` on the existing entry — **mutates the append-only
prefix and correctly trips `check_ledger_append_only.py`**.

**What was done instead.** A NEW entry was appended, flagged `preventive`, whose description names the
earlier entry and states that it supersedes *by annotation*, not by replacement. Both entries remain.
This is the only move the append-only property permits, and the property is worth more than the tidiness.

**The cost, stated so it is not discovered during scoring.** The count of `preventive` entries now
over-counts by one relative to the count of preventive *acts*. **Anyone tallying preventives must
de-duplicate by artifact, not by entry.** Recorded in
`../retrospective/PREVENTIVES_ARE_ACTS_NOT_TAKEN.md` as consequence 2, because that is where the
tallying will actually happen.

**The general rule this establishes.** An amendment that adds a field can only be applied *going
forward*. Entries predating an amendment are `unrecorded` for that field — never backfilled, never
inferred. The same principle already governs `actor` (AMENDMENT 1) and `via` (AMENDMENT 2), where the
gate pins the cutoff to the amendment's actual instant precisely so that pre-amendment entries are not
convicted. This is that rule meeting its first *post*-amendment omission, and the answer is the same:
the record says what it said, and corrections are additions.
