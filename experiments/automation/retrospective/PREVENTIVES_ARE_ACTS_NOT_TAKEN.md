# The preventives are acts NOT taken — read this before auditing the record

**Written 2026-07-31, after the fourth preventive. For whoever performs the retrospective audit.**

## The pattern

Amendment 3 added a `preventive` flag for catches that stopped an act *before it executed*. Four have
now been logged, and looking at them together they share a property that the flag's original wording
did not anticipate:

| # | the act NOT taken |
|---|---|
| 1 | a session that was **not run** — the pre-registered budget was exhausted and the work stopped |
| 2 | a countersignature that was **not accepted as written** — the ratified wording would have tripped the append-only gate |
| 3 | a proof that was **not re-derived** — the reachable-lemma index found it already existed |
| 4 | an arm index that was **not spent** — AI-selected work logged as `baseline` rather than as E2 session 2 |

Add the two standing orchestrator commitments and the shape is unmistakable: a trap set that is **not
authored** by the system under test, and an answer key that is **not committed** to the repo before
scoring.

**The discipline's highest-value catches are increasingly things that did not happen.**

## Why this matters for the audit specifically

**An audit of the artifacts will find none of them.** There is no diff for a session that was not run,
no commit for a proof that was not re-derived, no schedule entry for an index that was not spent. They
leave no trace in the code, the build, the test count, or the git history. They are visible **only
because the refusal was written into the ledger at the moment it was made** — which means the ledger
is not merely a record of this class of catch, it is the *sole* instrument that can see it.

Call it the dark matter of the experiment: inferred from the ledger's pointers, invisible in the
artifacts, and entirely absent from any measurement that counts outputs.

## Three consequences the auditor should carry

1. **Do not treat a low-artifact session as a low-value session.** The session that produces nothing
   because it correctly declined to produce anything is the one this program most wants to count. The
   live E1 gate is explicitly blind to sessions never logged (see `check_ledger_append_only.py`), and
   this is the class most likely to go unlogged, because there is nothing to commit alongside it.

2. **Preventives cannot be flagged retroactively.** The ledger is append-only, so an entry logged
   without `--preventive` cannot be amended in place. Preventive #4 was re-logged as a *new* entry that
   annotates the earlier one; both remain. When counting, **de-duplicate by artifact, not by entry** —
   otherwise the re-log inflates the count of the very thing it was correcting. See `../ledger/MIGRATIONS.md`.

3. **This pattern is a hypothesis, not a finding.** Four instances, all logged by the same AI, all in
   one week, and self-classified. The auditor should treat "the highest-value catches are acts not
   taken" as a claim to be tested against the retrospective sample, and should be alert to the obvious
   failure mode: **an act not taken is the cheapest thing in the world to claim credit for.** A
   preventive with no evidence that the act was ever actually about to happen is indistinguishable
   from a story told afterwards. Where the record does not show the act being genuinely underway,
   score it as unrecoverable rather than as a preventive.

Consequence 3 is the one that most needs a human. The AI cannot grade the sincerity of its own
refusals, and that is the same conflict this directory's `TEMPLATE.md` records for the audit as a whole.
