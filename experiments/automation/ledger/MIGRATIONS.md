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


## 2026-07-31 (later the same day) — CORRECTION: the cost above was stated BACKWARDS, and the real defect is larger

The entry above says *"preventive ENTRIES now over-count preventive ACTS by one."* **That is wrong in
direction and wrong in magnitude.** Corrected here rather than edited above, per this file's own rule
that corrections are additions.

**Measured, by two independent derivations:**

| derivation | count |
|---|---|
| entries with `preventive: true` | **3** |
| entries whose description names a decline/refusal/stop-before-execution | **13** |

The flag **under**-counts by a factor of four. It does not over-count at all.

**The real defect, which the miscount was hiding.** `preventive` is an **optional** field. The
validator never requires it — unlike `actor` (AMENDMENT 1) and `via` (AMENDMENT 2), which are required
after a pinned instant and whose absence is a gate failure. An optional flag applied ad hoc by the same
party that writes the entries produces a number that **is not a count of anything**. Ten of the thirteen
preventive-shaped acts are unflagged, including several logged *after* AMENDMENT 3 took effect.

**Therefore: any tally of preventives from the flag alone is invalid**, and
`../retrospective/PREVENTIVES_ARE_ACTS_NOT_TAKEN.md` consequence 2 must be read with this correction —
its de-duplication advice is still right (it prevents double-counting the one act that has two entries),
but the "over-count by one" premise is not.

**Two ways to fix it, neither taken unilaterally because both change the protocol:**

1. **Make `preventive` required for `correction`/`taste` after a pinned instant**, exactly as AMENDMENT
   2 did for `via`. Gate-enforced, consistent going forward, silent about the past — the established
   pattern.
2. **Have the retrospective derive preventives from descriptions rather than the flag**, and treat the
   flag as advisory. Cheaper, and it recovers the ten already-logged acts, but it puts a judgement call
   back into the instrument.

**Recommendation: (1), with the retrospective doing (2) for the pre-cutoff backlog.** This needs an
orchestrator countersignature — the party that would benefit from a higher preventive count should not
be the party that decides how preventives are counted.

**How this was caught.** Not by a gate. By cross-deriving a count two ways during an unrelated status
sweep, which is the standing rule that a correct-looking output does not evidence a sound mechanism.
The number `3` looked entirely reasonable and would have gone into a summary unchallenged.
