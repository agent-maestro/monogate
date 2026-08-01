# Research-automation experiment — pre-registered protocol

**Status (2026-07-31):** E1 **live** — 16 sessions, 25 findings, 52 interventions. E2 **running** — 1
of 10, schedule frozen. E5 **closed** — 8 of 8, plus continuation arms E5-ter and E5-quater at 6 of 6.
E3 and E4 **not started** (both orchestrator-gated). Per-arm detail below; this line is a summary and
the arm sections are authoritative.
**Instruments built by:** AI (Claude Opus 5). **Experiments run by:** orchestrator, except the arms
explicitly assigned to `E2-ai` and the `baseline` sessions.

**The header used to read "Nothing in this file has been measured. No experiment has run."** That
stopped being true on 2026-07-30 and was not updated until 2026-07-31 — a stale status line surviving
its own subject for a full day, in the file whose second paragraph warns about exactly that. Recorded
rather than quietly replaced, because the failure is the point: **prose does not fail a build.** The
only load-bearing fix is `status.py`, which derives arm status from this file — and it faithfully
reported "E2 NOT STARTED" the day after E2 session 1 ran, because it reads the prose. **A deriving tool
inherits the staleness of what it derives from.**

Prediction slots as of 2026-07-30: **E2's is FILLED** (orchestrator, before any session, with its
disconfirming observation named). **E5's are DRAFTED BY AI and require countersign** — see E5, and read
the provenance note before the drafts. All others empty. The header used to read "every slot is empty
by design"; that stopped being true the moment one was filled, and a status line that outlives its
subject is the failure this project files under *the word preceding its evidence*.

---

## The claim under test

> **The inner loop of mathematical research (prove/refute a stated conjecture) is automating; the outer
> loop (select targets, judge significance, catch plausible-wrong and misformalized statements) is not.**

This is a claim about *this project*, testable with *this project's* record. It is not a claim about AI
in general, and the arms below are scoped so that a negative result is informative rather than merely
embarrassing.

## Publication commitment

> **Results are published whichever way they cut. A negative result is a finding and is filed as one.**

The most likely negative results, named in advance so their arrival is not reinterpreted: the outer loop
may turn out to be automatable (E2 shows no arm difference); the inner loop may turn out *not* to be
automated (E5 fails, or E3 shows the pipeline passing false statements); or the ledger may show that what
we call "taste" is mostly mechanical relay (E1).

## House rules binding this program

1. **Pre-registration before data.** Bars, predictions and thresholds are committed before the first
   measurement they judge. Amendments are recorded with date and reason, never silent.
2. **Every gate ships with its firing specimen** — a demonstrated failure *and* a demonstrated pass, in
   the same commit. A gate with no firing specimen is UNVALIDATED, not passing.
3. **Enumerate-then-count.** Summary counts are computed by the tool that enumerated. No hand-written
   totals anywhere in this directory.
4. **UNAVAILABLE is failure.** A metric that cannot be derived reports as instrument failure, never as
   zero. A zero and an unmeasurable are different facts.
5. **Append-only records.** Ledgers and changelogs only grow; a CI gate diffs against git history.
6. **No claim without an artifact.** Anything a report asserts links to the file that shows it.

---

# E1 — Intervention ledger

**Status: LIVE at commit.** This is the only arm whose data collection begins immediately, because it
measures ordinary work rather than a designed intervention.

**Hypothesis.** Human interventions concentrate in *direction*, *correction* and *taste*; the
*mechanical* share is small and shrinking. If the claim under test is true, findings should track
direction/taste interventions rather than session count.

**Measurement.** Every session logs its interventions by kind and its findings by class. Reported as
ratios per session and cumulatively, plus a findings-per-session time series.

### Definitions — these ARE the measurement

| kind | means |
|---|---|
| `direction` | chose or changed **what to work on** |
| `correction` | caught an **error** in AI output |
| `taste` | judged worth / not-worth, significance, or smell — **without an error being present** |
| `mechanical` | ran or relayed **without judgment** |

The `taste`/`correction` boundary is the one that matters: a `correction` requires an error to exist. If
the human said "this is fine but boring", that is `taste`. If they said "this is wrong", that is
`correction`. **Boundary cases are logged with a `?` flag rather than dropped** — a dropped boundary case
is a silent thumb on the scale, and the flag lets the ambiguous ones be counted separately later.

| finding class | means |
|---|---|
| `closure` | a stated conjecture proved or refuted |
| `surprise` | something true that nobody asked for |
| `falsification` | a claim of ours shown false |
| `dead_end` | a route closed off, negatively informative |

### Known blindness

The append-only gate can detect a *modified* or *deleted* entry. It **cannot detect an entry that was
never written.** An unlogged session is invisible to this instrument, and that is the failure mode most
likely to bias E1 — the sessions least likely to get logged are the boring ones, which would inflate the
findings-per-session ratio. Partial mitigation: a session with findings but **zero** logged interventions
is flagged `SUSPECT` by the gate. That catches "logged the win, skipped the work", not "skipped the
session".

### AMENDMENT 1 to E1 — entries record WHO intervened (2026-07-30)

**Recorded after E1's first session, before the ledger had enough data to be quoted.**

**The defect.** The four kinds record *what* happened, never *who did it*. But the claim under test is
specifically that the **human** outer loop is not automating. On E1's first real session, both `taste`
entries were **AI self-catches** — the AI noticing its own vacuity risk and its own duplicated mistake.
Under the original schema those would have counted as `taste`, and the report would have shown
"taste leading, mechanical zero" — the exact shape the hypothesis predicts, **produced by the wrong
agent.**

> **A ledger that records that taste HAPPENED without recording WHO exercised it lets AI self-catches
> confirm the human-outer-loop hypothesis for the wrong reason.** That is not a small bias; it is the
> measurement quietly answering a different question than the one asked.

**The change.** Entries carry `actor : human | ai | unclear`. The CLI requires it. `report` prints a
by-actor breakdown and, separately, a **HUMAN-ONLY intervention mix** — the figure the central claim
actually rests on.

**Pre-amendment entries are NOT retro-labelled.** Four entries predate this and carry no `actor`. They
stay exactly as written — the ledger is append-only, and rewriting history to make a cleaner dataset is
the one move the whole program forbids. They appear in the report as **`unrecorded`, in their own
bucket, never folded into any actor**. An unrecorded actor and a known actor are different facts, and
the report keeps them different. That is UNAVAILABLE-is-not-zero applied to the ledger's own past.

**What this does not fix.** `actor` is self-reported by whoever runs the CLI. Nothing verifies it. It
converts an invisible bias into a recorded attestation — the same grade as E2's arm-label honesty, and
it belongs on the same list of limits no gate here can cover.

### NOTE CONVENTION (not a schema change) — preventive vs corrective catches

A catch that stops an act before it executes is a different event from one that finds an error after
it did. On 2026-07-30 the pre-registered E5 budget stopped a session from starting — the structure
prevented a boundary crossing rather than catching a mistake. **That is the first observation of the
thing pre-registration theoretically buys: cheaper than any catch is the mistake that never executes.**

Recorded as a **note convention in the description**, deliberately not a schema field: preventive
catches are rare enough that a fifth column would be mostly empty, and an empty column invites being
filled for the sake of it. Prefix the description with `PREVENTIVE:` or `CORRECTIVE:` on catch-class
entries where the distinction is real.

**If preventive catches recur, they become their own finding** about what the discipline is for — at
which point a schema field is warranted and this note is the evidence that it was earned rather than
guessed.

> **SCORED 2026-07-31: they recurred, the field was added (AMENDMENT 3), and the field does not work.**
> A cross-derivation during an unrelated status sweep found **3** entries carrying `preventive: true`
> against **13** whose descriptions name a decline, a refusal, or a stop-before-execution. The flag
> under-counts by a factor of four, because — unlike `actor` and `via` — it is **optional and never
> required by the validator**, so it is applied ad hoc by the same party that writes the entries.
> **Any tally of preventives from the flag alone is invalid.** The prediction in this paragraph was
> right about recurrence and wrong about sufficiency: earning a field is not the same as enforcing it.
> Fix options and a recommendation are in `ledger/MIGRATIONS.md` (2026-07-31, second entry); the choice
> needs an orchestrator countersignature, since the party that benefits from a higher preventive count
> must not be the party that decides how preventives are counted. Entries logged before this convention are unmarked, in the same way pre-Amendment-1 entries
carry no `actor`: the past is not relabelled.

### AMENDMENT 4 to E1 — `preventive` becomes a REQUIRED TERNARY (2026-07-31)

**The defect, measured rather than suspected.** AMENDMENT 3 added `preventive` as an *optional*
boolean. A cross-derivation during an unrelated status sweep counted it two ways:

| derivation | count |
|---|---|
| entries with `preventive: true` | **3** |
| entries whose description names a decline / refusal / stop-before-execution | **13** |

**A 4× undercount.** Unlike `actor` and `via`, the field was never required, so it was applied by
whoever remembered it — and the party writing the entry is the party a high preventive count flatters.
**An optional self-reported flag is not a count of anything.**

**The change.** `--preventive` / `--not-preventive` become a required, mutually exclusive pair on
`correction` and `taste`. The CLI refuses the entry without one; the gate fails a catch-class entry
logged after the pinned instant with no declaration. **Absence and `false` are different facts, and
only one of them is a measurement.**

**The past is not touched.** Entries predating the amendment report as `undeclared`, never as `false`,
and `report` prints that count separately with a `[PARTIAL]` marker directing any pre-amendment tally to
derive from descriptions instead. Same treatment as `actor` (AMENDMENT 1) and `via` (AMENDMENT 2); the
cutoff constant is **measured from the clock at amendment time, not typed**, because a rounded cutoff
convicted two innocent entries the first time AMENDMENT 1 ran.

**Firing specimen:** `specimens/amendment4/` — one entry, one field of difference, convicting and
acquitting. Its convicting fixture is timestamped an hour ahead so it cannot expire into a false pass.

**What this does not fix.** Whether a catch *truly* stopped an act before it executed is still
self-reported and unverifiable. This converts a silently-omitted field into a forced attestation — the
same grade as `actor`, and it belongs on the same list of limits no gate here can cover. **An act not
taken remains the cheapest thing in the world to claim credit for.**

### AMENDMENT 5 to the prediction discipline — a straddle is not a binary call (2026-07-31)

**The defect, isolated from four scored predictions.** The record reads 1-for-4, but the record is the
less useful artefact. **The taxonomy is:**

| session | outcome | defect class |
|---|---|---|
| E2 session 1 | predicted `closure`, got `falsification` | **miss-of-model** — the mechanism was wrong |
| E5-quater target 2 | route hit its halt point | **halt-point hit** — not a prediction failure at all |
| SKY130 area | predicted over 4 tiles, was | **win** |
| narrow kernel | predicted W=12 fails, it passed | **miss-of-conversion** |

**The taxonomy matters more than the record, because the repairs differ.** A miss-of-model means the
reasoning was wrong and the fix is better reasoning. A **miss-of-conversion** means the reasoning was
*right* and the wrong side of it was reported — the narrow-kernel prediction said the window would
straddle the bar at "two to three octaves", which is exactly what happened, and then called it a fail.
**The error lived in the conversion from model to binary call, not in the model.**

**The change.** When the mechanism itself says *straddle*, the honest pre-registered prediction is:

> **MARGINAL — direction uncertain.**

with the straddle's bounds stated. **Forcing a binary call on a straddle manufactures a coin flip and
then scores it as judgement**, which corrupts the record in both directions: a lucky call reads as
insight, an unlucky one as a reasoning failure. Neither is true, and the prediction record is supposed
to measure reasoning.

`MARGINAL` is scored as **correct if the outcome lands inside the stated straddle**, and wrong if it
lands outside — which is a claim about the model, and is the thing actually worth measuring.

**What this does not license.** `MARGINAL` is available only when the *mechanism* produces a straddle
before the measurement. It is not a hedge to be reached for when a prediction feels uncomfortable, and
a pre-registration that predicts `MARGINAL` on everything has predicted nothing. The straddle's bounds
must be stated, and stating them is what makes the hedge falsifiable.

### The append-only argument, recorded because the tempting middle path is seductive

A "purely additive mutations are fine" exemption was available and was rejected. The argument, in one
sentence:

> **An added key can change how the existing ones read.**

Append-only protects *bytes* because meaning supervenes on bytes. Any gate that permits byte changes
while trying to police meaning directly has taken on an undecidable job — it must decide whether a new
field reinterprets an old one, which is not a question about the file. So the rule stays byte-level and
strict, and additions that cannot be made in place are annotated **from outside**, in
`ledger/MIGRATIONS.md`, with both counts printed separately. That is the demotion rule at the schema
level.

### Constitutional symmetry, completed 2026-07-31

The rule set has now overridden **both** principals within one week:

| date | overridden | how |
|---|---|---|
| 2026-07-30 | the orchestrator's **instruction** | a generic "proceed" could not start a session past an exhausted pre-registered budget |
| 2026-07-31 | the orchestrator's **instruction** | "proceed into all of that" could not authorise trap authoring or retrospective classification against a contamination rule |
| 2026-07-31 | the co-author's **ratified wording** | a countersigned migration instruction was declined because the gate would have convicted it |

**A constitution that binds only the junior party is a policy.** This one survived its authors in both
directions, which is the only test of the distinction that means anything. All three are recorded as
`preventive` — the class that exists because *cheaper than any catch is the mistake that never
executes*.

### AMENDMENT 2 to E1 — catch-class entries record WHERE the catch fired (2026-07-30)

**Recorded the same day as Amendment 1, after it made the underlying issue visible.**

Amendment 1 revealed that AI self-catches were about to be counted as evidence for human taste. The
fix made *who* visible. But it exposed a sharper question, and the honest reading of one session is
that **the claim as originally stated may be wrong in an interesting way**:

> The live question is not *"who catches errors"* — plausibly the AI does, increasingly — but
> **where does the chain terminate.**

Every AI self-catch logged today fired **inside a structure a human built and ratified**: the specimen
doctrine that forced the convict run, the pre-registration that made the E5 baseline checkable, the
session protocol that pointed a gate at its own threshold. The human interventions are fewer, higher,
and load-bearing in a different way — selection, ratification, and the standing rules that make AI
self-catching possible at all.

**If E1 ends up measuring a thin human layer and a thick AI layer, with the thin layer holding the
termination points, that is not the hypothesis failing. It is the hypothesis being refined into its
true form** — which is what an instrument is for. But the refined form needs a distinction the
original schema could not make:

| `via` | means |
|---|---|
| `structural` | the catch fired **inside a human-installed structure** — a specimen convicting, a gate refusing, a pre-registered bar objecting |
| `spontaneous` | the catch **arose unprompted** in open work, with no structure behind it |

**This is the discriminator.** An AI catch that fires because the discipline made it fire is *the
discipline executing*. An AI catch with nothing behind it is *the outer loop genuinely automating*.
Reporting AI catch counts without this axis would conflate the two, and the conflation would favour
the more impressive reading.

Required on `correction` and `taste` entries; the CLI refuses without it and the gate flags it.
**Cheap to record today, impossible to reconstruct later** — which is why it lands now, at n=5, rather
than at analysis time.

**Abandonment criteria:** `PREDICTION: [to be filled by orchestrator before first report]`
**Pre-registered prediction:** `PREDICTION: [to be filled by orchestrator before first report]`

---

# E2 — AI-selected frontier ablation

**Status: RUNNING — 1 of 10 sessions. Schedule FROZEN (`e2_schedule.lock`) at session 1.**
Session 1 (`2026-07-31-e2s1`, arm `E2-ai`): 2 findings, 1 a surprise, **prediction WRONG** —
pre-registered `closure`, got `falsification`. That runs *against* E2's own pre-registered prediction
at n=1. Sessions 2–5 and 7 are `E2-human` and await orchestrator-named targets; the contamination rule
requires they be named without reading `e2_sessions/2026-07-31-e2s1.md`.

**Hypothesis.** Sessions whose target was selected by a human produce more findings — and more
*surprises* specifically — than sessions whose target was selected by the AI. If the outer loop is not
automating, the human-selected arm wins on finding quality even when the inner-loop work is identical.

**Measurement.** Findings per session, falsified-claim rate, and surprise rate, **by arm**. Arms are
`E2-ai` (AI names the target) and `E2-human` (orchestrator names the target).

**Design.** `e2_schedule.py` generates a session-assignment schedule once, records its seed, and commits
it. The schedule is **frozen at first use**: `check_e2_schedule_frozen.py` fails if the schedule file's
hash changes after any E2 session has been logged. Choosing arms as you go, in a study you are also
scoring, is the failure this prevents.

**Contamination rule.** The AI arm must select its target without having seen the human arm's target
list for the same period, and vice versa. If both arms are run in one context window, the arm assignment
is contaminated and the sessions are void.

**Per-session pre-registration** (`e2_session_template.md`): the target, the expected finding, and the
predicted class are written **before** the session and scored after. A session with no pre-registration
file is not scorable and is excluded — recorded as excluded, not silently dropped.

### PRE-REGISTERED PREDICTION — orchestrator, 2026-07-30, before any E2 session

> **AI-selected sessions produce more closures and fewer surprises. The catches where the win was
> smelling that a prior session's caveat was load-bearing concentrate in the human-selected arm.**

**Quantitative form, which is the part that can be wrong:**

> **If surprise-rate is indistinguishable between arms over the first ten sessions, the prediction is
> wrong in the direction that matters** — i.e. the outer loop is more automatable than this program's
> central claim assumes, and that is the finding.

Recorded before the schedule exists, before any session runs, and stated so that the disconfirming
observation is named rather than left to interpretation afterwards. Provenance: orchestrator,
in-session, 2026-07-30.

### E2 abandonment — COUNTERSIGNED 2026-07-31, with both clauses

| slot | PRE-REGISTERED VALUE | countersigned |
|---|---|---|
| **abandonment** | Abandon after **10 sessions** if the arms are INDISTINGUISHABLE, defined below. | ✅ orchestrator, 2026-07-31 |

**CLAUSE 1 — "indistinguishable" is defined NOW, before any data.** A stopping rule whose trigger term
is defined after the data exists is the post-hoc flexibility the rule exists to prevent, one level up.
At n=10 there is no statistical power worth pretending about, so this is an **effect-size bar, not a
significance test**:

> Arms are **indistinguishable** iff BOTH:
> * the difference in **findings-per-session means** is **< 25% of the pooled mean** — a *relative*
>   margin, because we have no base rate to anchor an absolute one; and
> * the difference in **surprise counts** across the arm totals is **< 1** — an *absolute* count,
>   because at five sessions per arm surprises are countable on one hand and a percentage would be
>   theatre.

**CLAUSE 2 — each exit carries its verdict.** A stopping rule that says when to stop but not what
stopping *means* leaves the interpretation to whoever writes the summary, which is the last place
discretion should live.

| exit | verdict recorded in the results section |
|---|---|
| indistinguishable at 10 | **PREDICTION FALSIFIED, CENTRAL CLAIM DAMAGED.** The prediction named ten sessions as its own disconfirmer. This exit is not a null shrug and is not "the study ended" — it is the recorded finding that the outer loop is more automatable than the claim assumes, published as one. |
| distinguishable at 10 | Continue to the schedule's horizon, **with the interim direction recorded** — including which arm led and by how much, so a later reversal is visible as a reversal. |

---

# E3 — Trap set

**Status: NOT STARTED. Traps not authored.**

**Hypothesis.** The pipeline catches SUBTLY_FALSE statements (the prover fails, gates fire) but does
*not* catch MISFORMALIZED ones — where the Lean statement is provable and true, and simply does not mean
the English claim. Misformalization is invisible to every gate we own, because every gate checks the
formal object.

**Measurement.** Per trap: which pipeline stages saw it (prover / gates / certifier / adversarial
review), the verdict at each stage, and **the stage that caught it — or `NONE`**. Reported as catch rate
by planted class and by stage.

**Planted classes.** `TRUE`, `SUBTLY_FALSE`, `MISFORMALIZED`. 20 slots.

### Contamination warning — verbatim, non-negotiable

> **Traps must not be authored by the same AI system under test, and must not enter any context visible
> to the system before evaluation. Trap authorship is an orchestrator task, possibly with a different
> model in an isolated session. An AI grading traps it wrote is the vacuous-test failure mode.**

This is why the traps are **not** authored in this commit and must not be authored by the assistant that
built this harness.

### Sealing mechanism

The answer key is `answer_key.json`, which **stays out of the repo** (orchestrator holds it) until
scoring. Its SHA-256 is committed in `e3_traps/manifest.json` *before any trap is evaluated*.
`score_traps.py` verifies the key against the pre-committed hash before scoring anything; **a key that
does not match is an invalid experiment and a hard failure**, not a warning. This makes "adjust the key
after seeing the results" mechanically detectable rather than a matter of trust.

**Abandonment criteria:** `PREDICTION: [to be filled by orchestrator before first run]`
**Pre-registered prediction:** `PREDICTION: [to be filled by orchestrator before first run]`

---

# E4 — External-statement formalization

**Status: NOT STARTED. No tooling built.**

**Hypothesis.** Formalizing a statement from a paper we did not write exposes misformalization risk that
our own statements do not, because our own statements were written by the same process that formalizes
them.

**Measurement.** Per run: does the Lean statement mean the paper's claim? Reviewed by a party that did
**not** write the formalization. Template: `e4_external_statement_template.md`.

**Contamination rule.** The adversarial statement-reviewer must not be the author of the formalization,
and should not be the same model instance. Self-review of statement fidelity is the same vacuous test as
self-authored traps, one level up.

**Abandonment criteria:** `PREDICTION: [to be filled by orchestrator before first run]`
**Pre-registered prediction:** `PREDICTION: [to be filled by orchestrator before first run]`

---

# E5 — Open-problem attempt: `1/x ∉ EML` at any depth

**Status: BUDGET EXHAUSTED 2026-07-30 — 8 of 8 sessions run. Bar CLEARED on both arms. Result below. THE UNDERLYING WORK IS NOT NEW — see baseline below.**

**Continuation arms E5-ter and E5-quater are also CLOSED — 6 of 6 sessions, 2026-07-31.** Both were
separately pre-registered against the same open problem after the original budget ran out. Seven
findings, **two pre-registered targets falsified by construction**, one halt point fired on schedule,
and `1/x ∉ EML` still open — better characterised, not closer to proved. See `E5B_RESULT.md` (E5-ter)
and `E5QUATER_RESULT.md` (E5-quater). **No further E5 sessions without a fresh pre-registration and a
fresh budget**: an arm that keeps spending its own remainder is an arm whose budget has become
decorative.

**Do not begin until all three slots (route, session budget, abandonment criteria) are filled and committed.**

### The prior recommendation, copied from the record

From `monogate-research/exploration/inv_x_not_in_eml_depth_1_2026_06_15/FINDINGS.md`, "Honest
recommendation":

> The general-depth claim is the same open problem the addition-closure and diff-closure attempts both
> ended on; **convergence on it is now three-way.** Next session priority: attempt the
> asymptotic-Hardy-field / Khovanskii-style structural argument for `1/x ∉ EML at any depth`, leveraging
> MachLib's existing asymptotic and Pfaffian scaffolding. If successful, this single result closes the
> addition-closure conjecture, the differentiation-closure conjecture, *and* the Lambert-W candidate 1
> question in one move.

From `monogate-research/exploration/eml_hardy_field_bridge_crack_2026_06_15/FINDINGS.md`, "The natural
next session" — route (b), the recommended one:

> Build a small asymptotic-class framework in MachLib. Start with: define `EventuallyConstant`,
> `EventuallyKOverX`, `EventuallyKExpX`, `EventuallyIterExpClass k`. Prove every `EMLTree.eval` falls
> into one of these classes by structural induction. Show `1/x` falls into `EventuallyKOverX 1`, disjoint
> from the EMLTree-image classes (because EML's K is always `exp(...)` of something positive).
>
> This route is harder but bridges to the general-depth claim. … Recommendation: (b), because (a)
> doesn't scale to depth 3 anyway.

### BASELINE — read this before filling any slot

**Route (b) was taken, and has been worked for 21 recorded sessions.** Measured 2026-07-30:

| | |
|---|---|
| prior sessions on this route | **21** (`exploration/eml_asymptotic_class_*`, phases 1–17 plus depth sweeps) |
| companion artifact | `machlib/foundations/MachLib/EMLAsymptoticClass.lean`, **4,315 lines** |
| latest recorded frontier | Phase 17 (2026-06-24): class-level closure matrix **11/25** |
| the general-depth claim | **still open** |

**Why this matters for pre-registration.** E5 is not a fresh attempt at a fresh problem. Pre-registering
a "route" that has already been walked for 21 sessions, or a session budget set as though from zero,
would produce a measurement of something other than what it claims to measure. The slots below must be
filled *relative to this baseline* — e.g. a budget expressed as sessions-from-phase-17, and an
abandonment criterion expressed in closure-matrix movement rather than in "did it work".

`TODO: orchestrator` — confirm phase 17 is still the frontier at the time E5 begins; the count above is a
2026-07-30 measurement of a record that continues to move.


### RESULT — E5, 8 sessions, against the pre-registered bar

**Recorded 2026-07-30, immediately on budget exhaustion, before any decision about continuing.**

| | pre-registered | actual |
|---|---|---|
| session budget | 8 from phase 17 | 8 (phases 18–25) |
| abandon if | **fewer than 3 cells AND no new structural mechanism** | **7 cells and 2 new predicates** |
| verdict | — | **bar cleared on both arms** |

Matrix **11/25 → 18/25**, against a reachable ceiling of 23/25 (two cells are provably
indeterminate). Rate 0.88 cells/session versus the 0.52 baseline the budget was derived from.

**The general-depth `1/x ∉ EML` claim remains open.** Seven cells is progress on the closure matrix,
which is the *instrument* for that claim, not the claim itself. Nothing here should be read as having
attacked the open problem directly.

**What the sessions actually produced, beyond cells:**

1. **An ordering nobody asked for.** The hypothesis a cell needs is monotone in how hard the dividend
   pulls: unbounded needs none, vanishing needs `0 < log d`, merely-bounded needs `1 ≤ log d`.
2. **Two of Phase 17's own labels were wrong** — its prose undercounted its table by a cell, and its
   "risky" deferral of two rows had aged out once class-level rules existed. Both found by re-reading
   the record against what is provable, not by new mathematics.
3. **A predicate pair** (`EventuallyAtMost` / `EventuallyAtLeast`) that Phase 17 had named as a
   hypothesis and that turned out to carry six of the seven cells.

**Continuing is a NEW pre-registration, not a continuation.** The budget was set relative to phase 17
and is spent. A further budget must be set relative to phase 25, with its own abandonment criterion,
and countersigned before the first session — otherwise the bar becomes a thing that moves when it is
about to bind, which is the failure the whole apparatus exists to prevent.

### Slots — COUNTERSIGNED 2026-07-30. E5 IS PRE-REGISTERED AND MAY BEGIN.

**Read the provenance line before reading the drafts.** E5 measures whether this loop can finish an
open problem. If the AI sets the bar it will be judged against, that is the instrument grading its own
exam — the same defect E3 exists to detect and the retrospective refuses to commit. So these are
**drafts with teeth, not pre-registrations.** They become pre-registered only when the orchestrator
countersigns, and the countersignature is what makes them binding.

| slot | PRE-REGISTERED VALUE | countersigned |
|---|---|---|
| **Route** | Continue route (b) from phase 17: close the class-level closure matrix, currently **11/25**. Do not restart the framework; do not switch to route (a) (the depth-2 brute-force sweep) — the record already shows it does not scale to depth 3. | ✅ orchestrator, in-session, 2026-07-30 |
| **Session budget** | **8 sessions from phase 17.** Rationale, from the baseline: the route absorbed 21 sessions to reach 11/25, ≈0.52 matrix-cells per session. 8 sessions is ~4 cells at the observed rate — enough to distinguish "still moving" from "stalled", and short enough that a stall is visible before it becomes sunk cost. | ✅ orchestrator, in-session, 2026-07-30 |
| **Abandonment criteria** | **Abandon if, after 8 sessions, the closure matrix has advanced fewer than 3 cells beyond 11/25 AND no new structural mechanism has been identified.** Both conditions, because cells-only would abandon a session that found the right idea and had not yet cashed it, and mechanism-only is unfalsifiable — every stalled session can claim to have learned something. | ✅ orchestrator, in-session, 2026-07-30 |

**Why the budget has teeth:** the baseline is a route that absorbed **21 sessions without resolving the
general-depth claim**. A criterion that cannot fire against that history is not a criterion. The draft
above fires on the observed rate, not on an aspiration.

**COUNTERSIGNED without amendment**, orchestrator, in-session, 2026-07-30. The drafts stand as
written and are now binding pre-registration: route (b) continued from phase 17, **8 sessions**,
abandon at **fewer than 3 closure-matrix cells AND no new structural mechanism**.

The provenance distinction still holds and is why this line exists: the bar was *drafted* by the AI
and *ratified* by the human. Had it been set and met by the same party, E5 would measure nothing about
either. **Session 1 of 8 is phase 18.**

---

## Scoring rubric (E2, and reused by E1's report)

| metric | definition | computed by |
|---|---|---|
| findings per session | count of `findings[]` ÷ sessions in arm | `ledger.py report` |
| falsified-claim rate | `findings[class=falsification]` ÷ findings | `ledger.py report` |
| surprise rate | `findings[class=surprise]` ÷ findings | `ledger.py report` |
| intervention mix | each `kind` ÷ total interventions | `ledger.py report` |

All four are **computed from the ledger**, never transcribed. A rubric number appearing in prose without
a tool that produced it is a house-rule violation and should be treated as one.

## Amendments

Append-only. Date, what changed, why. Empty at commit.

| date | change | reason |
|---|---|---|
| 2026-07-30 | E1 catch-class entries gain `via` (structural/spontaneous) | Amendment 1 made WHO visible and exposed the sharper question: not who catches, but where the chain terminates. Every AI catch so far fired inside a human-installed structure — a different event from one arising unprompted, and only `via` separates them after the fact. See E1 Amendment 2. |
| 2026-07-30 | E1 entries gain `actor` (human/ai/unclear) | The four kinds recorded what happened, never who. E1's first session logged two `taste` entries that were AI self-catches; unattributed, they would have shown the hypothesis's predicted shape produced by the wrong agent. Pre-amendment entries are not retro-labelled — they report as `unrecorded`, in their own bucket. See E1 Amendment 1. |
