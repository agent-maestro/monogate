# Firing specimens — every gate in this directory, both directions

> **A gate with no firing specimen is UNVALIDATED, not passing.** Doctrine and format inherited from
> `monogate-research/electronics_intake/tools/GATE_REGISTRY.md`, which records the three incidents that
> produced the rule (a gate firing inverted, a gate that never fired, and documentation asserting a call
> that did not exist).

All demonstrations below were run 2026-07-30, on the code in this commit.

---

## `score_traps.py` — the E3 seal

**CAN-CONVICT.** A key with one class flipped after sealing:

```
committed sha256 : 8fa9...  (from manifest.json, written before evaluation)
key sha256       : 4c1e...  (tampered)

[INVALID EXPERIMENT] the key does not match the hash committed before evaluation.
NOTHING IS SCORED.
E3 TRAP SCORING: HARD FAILURE — seal broken            exit 1
```

**CAN-ACQUIT.** The sealed key:

```
SEAL INTACT — the key is the one sealed before any trap was evaluated.
E3 TRAP SCORING: SEAL VERIFIED                          exit 0
```

**UNAVAILABLE-IS-NOT-ZERO.** Sealed key, no evaluation records:

```
[UNAVAILABLE] no evaluation records at e3_traps/records.
  A trap set with no records is unmeasured, NOT a score of zero.
                                                        exit 1
```

The specimen manifest was **removed** after the demonstration: the real trap set must be authored by
the orchestrator, not by the assistant that built the harness. See PROTOCOL.md E3.

---

## `check_ledger_append_only.py` — the E1 ledger

**CAN-ACQUIT** (this commit, empty ledger):

```
E1 LEDGER GATE: PASS — 0 session(s), 0 suspect (non-blocking).
  Blind to: sessions never logged at all, and to whether a kind was classified honestly.
                                                        exit 0
```

**CAN-CONVICT — and the specimen found a bug in the gate.**

First run of the convict demonstration: a committed ledger entry was mutated in place, and the gate
**PASSED**.

Cause: `git ls-tree` was invoked with `cwd=HERE` while being handed a *repo-root-relative* pathspec.
Git resolves pathspecs against the working directory, so it looked for
`experiments/automation/experiments/automation/...`, matched nothing, compared nothing, and reported
clean. **The check was not weak — it was pointed at an empty set and could not tell the difference
between "nothing changed" and "nothing examined".** Fixed by running `ls-tree` and `git show` from the
repository root, and the gate now prints how many files it compared so an empty comparison is visible
rather than silent.

After the fix, three convicting branches demonstrated against the committed fixture:

```
# prefix entry mutated
FAIL  FIXTURE-append-only.json: existing entries were MUTATED — append-only means the
      prefix is immutable, not merely that the file grew
    1 file(s) at HEAD compared
E1 LEDGER GATE: FAIL — 1 error(s)                       exit 1

# file deleted
FAIL  FIXTURE-append-only.json: existed at HEAD and is now GONE — ledgers are append-only
E1 LEDGER GATE: FAIL — 1 error(s)                       exit 1
```

**CAN-ACQUIT**, fixture restored:

```
    1 file(s) at HEAD compared
E1 LEDGER GATE: PASS — 1 session(s), 0 suspect          exit 0
```

The fixture lives in `specimens/ledger_fixture/` and is checked by its own CI step, so the append-only
branch stays validated on every push. It is deliberately **not** in `ledger/`: a specimen that
contaminates the dataset it validates is not a specimen, and E1's ratios must not include fixture rows.

**SUSPECT branch, demonstrated:** logging a finding into a session with zero interventions prints the
warning at write time and is flagged by the gate. Verified during CLI round-trip.

---

## `check_e2_schedule_frozen.py` — the E2 schedule

**CAN-ACQUIT** (pre-registration phase, no schedule and no E2 sessions):

```
no schedule yet, no E2 sessions yet — nothing to freeze.
E2 SCHEDULE FREEZE GATE: PASS (pre-registration phase)  exit 0
```

**CAN-CONVICT.** Two convicting branches exist in code and are **not yet demonstrated**, because both
require an E2 session to have been logged, and logging one before the protocol's prediction slots are
filled would violate house rule 1:

- E2 sessions logged with **no schedule file** → FAIL.
- Schedule hash **differs from the lock** after freeze → FAIL.

**Both branches are UNVALIDATED until the first E2 session exists.** Stated rather than assumed: this
gate currently has a demonstrated pass and no demonstrated failure, which by this project's own rule
means it is not yet known to be a gate.

`TODO: orchestrator` — demonstrate both convict branches at E2 launch, in the same commit as the first
E2 session, and update this file.

---

## `check_ledger_append_only.py` — AMENDMENT 1 actor check (added 2026-07-30)

**CAN-CONVICT.** A post-amendment entry with no `actor` (the CLI bypassed):

```
FAIL  FIXTURE-append-only.json: entries[2] logged after AMENDMENT 1 with no actor — the
      claim under test is about the HUMAN outer loop, so an unattributed entry cannot
      support it
E1 LEDGER GATE: FAIL — 1 error(s)                       exit 1
```

**CAN-ACQUIT**, `actor` supplied:

```
E1 LEDGER GATE: PASS — 1 session(s), 0 suspect          exit 0
```

**The first cutoff was wrong and the specimen caught it.** `AMENDMENT_1_TS` was initially a rounded
hour (`"2026-07-30T18"`), which convicted two entries logged *before* the amendment existed — a gate
punishing the past for not obeying a rule that did not yet exist. Pinned to the amendment's actual
instant instead. A guessed threshold in a time-sensitive check is the same class as a guessed pathspec:
it decides cases it was never shown.

**Blind to:** whether the self-reported `actor` is true. Nothing verifies it. The amendment converts an
invisible bias into a recorded attestation — same grade as E2's arm-label honesty, and on the same list
of limits no gate here can cover.
