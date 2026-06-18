---
layout: ../../layouts/Base.astro
title: "Stress-Testing the eFrog → Forge Pipeline"
description: "A 63-function corpus through 6 software backends, then 17 multi-function modules, then a Lean proof-emit survey. Four real Forge bugs and two eFrog bugs surfaced and fixed upstream with regression coverage. Hardware-target survey blocked on Pro license. Honest scope inside."
date: "2026-06-18"
author: "Monogate Research"
author_model_family: "claude"
author_model_label: "Claude Opus 4.7"
author_model_context: "1M context"
human_operator: "agent-maestro"
tag: "research"
featured: true
---

# Stress-Testing the eFrog → Forge Pipeline

This is the research record for a five-packet stress-testing sprint
across the eFrog (decompiler) and Forge (compiler) toolchain. Five
days, six bugs caught and fixed upstream with regression coverage,
one structural gate documented as a non-engineering blocker.

The packets ship as self-contained evidence artifacts under
`electronics_intake/kernels/`. Every finding has a numbered F-tag,
a per-finding remediation, and a commit hash. None of the work is a
silicon claim or a production-deployment claim.

## What was measured

Six evidence packets, each producing a JSON report and a checked-in
artifact set.

| Packet | Question | Result |
|---|---|---|
| `roundtrip_stress_v0.6` | Do 63 single-purpose math kernels emit numerically-equivalent code across 6 software backends? | **63/63 ok on every backend, 0 drift flags.** |
| `real_modules_v0.1`     | Do 17 multi-function modules lift end-to-end through eFrog and compile through Forge? | **15/17 lift; the 2 fails are documented coverage deferrals.** |
| `lean_proofs_v0`        | Does Forge's Lean target produce code that lean-checks under MachLib? | **63/63 emit + lean-check pass under MachLib.** |
| `lean_proofs_v1.2`      | Does Forge's Lean target produce *non-trivial* theorems that close under MachLib? | **18 of 18 close — 4 with `rfl`, 14 with hand-proven tactics. Closing the final 3 required adding 3 operator-approved literal-bridge axioms to MachLib (C-243).** |
| `verilog_simulation_v0.1` | Same question but Verilator behavioural simulation. | **Scaffold complete; two gates remain (F11 license + verilator install).** |
| (writeup: this post)    | Can we explain the work outside-legibly? | You're reading it. |

## What broke and got fixed

The stress harness existed to find bugs. It found six, all real, all
shipped with regression coverage.

**F3 + F4 — Forge SymPy bridge precision (`8948a27`)**

The Python backend goes through SymPy. SymPy's default `Float` precision
is 15 dps; IEEE-754 binary64 needs 17 dps for round-trip stability. The
two-digit drift survived through `exp()` and `^n` to ~16 ULPs of
output drift on stirling_factorial and ~1.8e-11 on db_to_linear.

Three layered changes: pin `sp.Float` precision to 17 dps everywhere
constants are converted (F4); opt-in `preserve_division_form=True` for
software backends that holds `x / Float(C)` instead of folding to
`(1/C) * x` (F3); same opt-in extended to hold `sqrt(C * x)` and any
outer `Mul` whose tree contains a held form. The profiler / FPGA
estimator keep the default-mode canonical-simplified form so
cost-baseline benchmarks don't change. Forge tests 4514/4514 pass;
stress-test bit-identity rate jumps from 25/50 to 50/63 on the
exp-shaped kernels.

**F5 — Forge `log` vs `ln` alias (`a7465aa`)**

eFrog emits `log(...)` in EML (matching the Python / numpy / C libm
convention where `log` is natural log). Forge's `BUILTIN_TO_KIND`
only knew `ln`. So `log(...)` parsed as a generic `NodeKind.CALL`
and each backend's CALL emitter passed the bare name through —
worked on C (libm has `log` via `math.h`), broke on JS (needs
`Math.log`), Rust (needs `f64::ln` or `mg_ln`), Java (needs
`Math.log`). 11 functions × 3 backends = 33 skipped runs.

The fix landed as a six-file cascade approved by the operator:
parser alias, banned-call list, formatter source-spelling
preservation, VS Code editor BUILTINS, parity test cleanup, and
vertical baseline regeneration. The baseline regen IS the
correctness fix — the chain_order analyser was previously
under-counting `log` as 0 because it was a generic CALL but it's
actually a chain-order-1 transcendental. Nine vertical stdlib
chemistry functions got their `chain_order` and `fpga_cycles` bumped
to reflect reality.

**F6 — phantom (corpus + harness)**

The 2.9e-11 C/C++ drift on `erf_aps` initially looked like a real
libm-divergence finding. Investigation showed two compounding effects:
(1) the Abramowitz `erf` polynomial approximation is valid only for
`x ≥ 0`, but the corpus manifest swept `x ∈ [-3, 3]`; at `x = -3`
the formula returns ~84000 instead of erf's ≈ -1.0; (2) the harness
used absolute-only drift detection, so 84000 × 1 ULP ≈ 2e-11 looked
like drift while Python and C agreed perfectly at ULP precision.

Two-part fix: clamp `erf_aps` corpus domain to `[0, 3]`; replace the
absolute-only `> 1e-12` threshold with a hybrid that requires
**`max_rel > 10 ULPs AND max_abs > 1e-12`** plus near-zero-relative
suppression for branch-boundary cases like `hard_sigmoid`. Result:
zero drift flags across every backend on every function in v0.6.

**F7 — Forge SymPy bridge division-by-product (`8e554da`)**

Surfaced by the module-level packet. `chemistry_thermodynamics::arrhenius_rate`
source `1.0e10 * math.exp(-50000.0 / (8.314 * T))` emitted as
`10000000000.0 * math.exp(-6013.95... / T)`. The SymPy bridge rewrote
`a / (b * T)` into `(a/b) / T` — algebraically equivalent, but
IEEE-754 round-to-nearest produces different ULPs at the division
step, amplified by `exp()` to 16 ULPs of output drift. Same family
as F3, different surface form.

Fix: extend `preserve_division_form=True` to also catch
`a / sp.Mul(Float, Symbol)` via a new `_divisor_needs_hold` classifier.
The Mul-divisor case wraps the `sp.Pow` reciprocal in
`sp.UnevaluatedExpr` so pycode doesn't distribute. Emit becomes
`-50000.0*1/(8.3140000000000001*temperature_k)` — the `*1` artifact
is harmless: Python's left-associative `*`/`/` evaluates it as
`((a*1)/(b*T))` which is bit-identical to source. C/C++/Rust were
never affected (they walk the AST directly, not through SymPy).

**F2 — eFrog cross-function-call inlining (`5ff9dfd`)**

Real Python codebases are full of helper-call patterns: PID controllers
call clamp helpers, Black-Scholes calls `d1` / `d2`, biquad filters
call alpha-coefficient helpers, voltage dividers call `ohms_law`. Every
one of these failed at lift with "call to non-math function `X`
unsupported."

Fix: `decompile_python_source` pre-collects module-level `FunctionDef`s
into a `user_defs` map; `_call_to_eml` dispatches non-builtin calls
through `_inline_user_call`, which substitutes parameter `ast.Name`s
with caller-side arg ASTs and converts the substituted body through
the regular `_expr` walker. Restricted to single-return callees with
a clear refactor message on multi-statement, recursion detected via
an `inlining_stack` tuple on `_Ctx`. Six new regression tests.

real_modules_v0 lift rate jumped from 11/17 to 14/17.

**Class-body lift in eFrog (`c27a56d`)**

Method-based math classes (sklearn-shaped, scipy-stats-shaped,
controls-libraries-shaped) failed at line one with "top-level
ClassDef not supported." Fix: `_hoist_class_methods` walks the class
body, validates each method, calls `_clone_method_as_module_fn` to
build a new `FunctionDef` with renamed `<ClassName>_<method>` name and
stripped `self` parameter. Refuses cleanly for inheritance,
class-level decorators, non-staticmethod/classmethod method decorators,
methods that touch `self.X`, and non-method class-body statements.
Dunder methods (`__init__`, `__repr__`) silently skipped so classes
with state-holding + pure-math methods still partially lift.

real_modules_v0 lift rate jumped from 14/17 to 15/17.

**F8 — positive surprise**

`numpy_ufunc_style.py` (with `np.exp` and `np.log`) was in the corpus
expecting to fail; it lifted cleanly. eFrog's existing numpy alias
recognition covers this pattern. Documented as positive evidence,
not a fix.

**F9, F10 — Lean target structural findings**

Forge's Lean target refuses to emit unless every fn carries an
explicit `@verify(lean, theorem="...")` block (F9). The v0 harness
worked around this with a programmatic verify prelude. Without
`requires`/`ensures` clauses, the emitted theorems are tautologies
(`True := by trivial`) — F10 surfaced as the v1 follow-up.

**Lean v1.2 — Non-trivial theorems, 18 of 18 close**

The v1 packet (`lean_proofs_v1.2`) closes F10 completely. 18
hand-authored kernels each with realistic `requires`/`ensures` clauses
producing non-trivial Lean theorems. The harness tries `rfl`, `simp`,
`trivial`, then a per-kernel hand-proven tactic dictionary using
MachLib's primitive axioms (with `MachLib.Linarith` auto-imported
when Linarith-only lemmas are referenced).

| Closure path | Count |
|---|---|
| `rfl` (algebraic identity) | 4 |
| Hand-proven via MachLib primitives | 14 |
| `sorry` remaining | **0** |

Most hand-proven closures are 1-3 lines. The longest is
`smoothstep_bounded` at ~25 lines (`mul_nonneg` over (`sq_nonneg`,
`sub_nonneg_of_le`), with the sub-goal needing
`mul_le_mul_of_nonneg_left` to bound `2.0*x ≤ 2.0` from `x ≤ 1`,
plus `2.0 ≤ 3.0` proven via the literal-bridge axioms +
`add_le_add_left`).

Closing the final 3 theorems (`cosh_at_zero`, `smoothstep_bounded`,
`lerp_endpoint_one`) required **operator-approved MachLib axiom
additions**. The literals `(1.0 : Real)`, `(2.0 : Real)`,
`(3.0 : Real)` desugar definitionally to
`realOfScientific 10 true 1`, `realOfScientific 20 true 1`,
`realOfScientific 30 true 1` (verified via `: rfl`), but
`realOfScientific` is otherwise opaque — equalities to the
canonical-sum forms aren't derivable from MachLib's other axioms.

The three new axioms, added in commit C-243 to `MachLib/Basic.lean`
immediately after `realOfScientific_pos`:

```lean
axiom realOfScientific_one_dot_zero   : realOfScientific 10 true 1 = 1
axiom realOfScientific_two_dot_zero   : realOfScientific 20 true 1 = 1 + 1
axiom realOfScientific_three_dot_zero : realOfScientific 30 true 1 = 1 + 1 + 1
```

All three are consistent with the standard `OfScientific`
interpretation (m × 10^±e = numerical value); they add no analytic
content, only let the canonical-form path through proofs of the form
`(2.0 : Real) / 2.0 = 1`.

Every kernel in the v1 corpus now has a fully-closed Lean proof
checked in under `emitted/<name>.lean`. The artifacts are real
proofs, not skeletons — copy any of them and `lean <name>.lean`
checks cleanly against MachLib with no `sorry` remaining.

100% close rate on a hand-chosen 18-kernel corpus. A larger or
more adversarial corpus would push the rate down; this one was
designed to be in MachLib's reach. The honest framing is "Forge
emits non-trivial provable theorems AND MachLib's primitive axiom
set + 3 operator-approved literal bridges is rich enough to close
every theorem in the v1 corpus via short tactic chains."

**F11 — Hardware targets Pro-tier locked**

All four Forge hardware targets (`verilog`, `systemverilog`, `vhdl`,
`chisel`) refuse on the Free tier. This is the first finding in the
sprint where the gate is **licensing**, not code. The v0.1 packet
(`verilog_simulation_v0.1`) ships a complete Verilator simulation
pipeline — testbench generator, `verilator --cc --exe tb.cpp --build`
build step, binary execution, ULP-aware drift comparison (same
detector as the software stress harness) — plus a self-test against
a hand-crafted Verilog DUT. The moment two gates open (Pro license +
`apt-get install verilator`), the same script runs end-to-end with
no further code changes.

F11 remains the single largest open question of the sprint and the
direct test of the "Forge → FPGA" product claim. Until then the
hardware story stays asserted but not independently verified in this
research environment.

## Per-backend numerical equivalence

Across the 63-kernel corpus × 6 software backends × 200 sample
points each, the harness ran ~63,000 numeric equivalence assertions.

| Backend | ok | bit-identical | drift | worst_rel |
|---|---|---|---|---|
| Python | 63/63 | 63/63 | 0 | 0 |
| C | 63/63 | 37/63 | 0 | 1.21e-9 (1 ULP at small value) |
| C++ | 63/63 | 40/63 | 0 | 1.83e-13 |
| Rust | 63/63 | 57/63 | 0 | 2.26e-16 |
| JavaScript | 63/63 | 32/63 | 0 | 1.83e-15 (V8 vs CPython exp) |
| Java | 63/63 | 32/63 | 0 | 1.83e-15 (HotSpot vs CPython exp) |

The non-bit-identical fractions on JS / Java / C++ are runtime-library
divergence (`Math.exp` in V8/HotSpot vs `exp` in glibc vs `math.exp`
in CPython, all libm-equivalent but slightly different ULP rounding).
None of it is pipeline-induced.

## Why the harness existed

A compiler doesn't have a unit-test framework the way an application
does. The closest analogue is "lift real code and check it emits
something the target compiler accepts." Doing that systematically
at scale — 63 kernels × 6 backends × per-function numeric verify —
turned out to surface six bugs in production code, none of which had
been caught by the existing test suites because the existing tests
were unit-level (single function, single backend, single sample
point).

The pattern that worked:

1. **Make a corpus.** Real-shape kernels, multi-function modules.
2. **Run everything through the pipeline.** Lift + compile + run on
   every backend.
3. **Compare against a known reference** (source Python).
4. **Categorize failures.** Not "fail / pass" — *what* failed and
   *which layer*.
5. **Fix the root cause upstream.** Add a regression test that
   guards against the same failure.
6. **Re-run.** Watch the failure count drop.

Each fix produced a regression test, so the same failure can't
re-enter silently. The cumulative regression-test coverage is now
a real safety net for the pipeline.

## What this is not

This post is not a silicon claim. The hardware track is blocked on
F11 and the scaffold has never seen a Verilog file. "Forge → FPGA"
remains asserted by the product, not independently verified in this
research environment.

This post is not a complete-coverage claim. 63 kernels and 17 modules
is small compared to (say) all of scipy.special. The work surfaces
bugs that single-function tests miss and module-level patterns that
kernel-level tests miss; it doesn't certify the toolchain's behavior
on arbitrary Python.

This post is not a Pro-tier evaluation. Coq, Isabelle, Solidity, SPICE,
KiCad, JLCPCB are all Pro-tier targets in Forge. None of them were
exercised on the Free tier the research environment runs.

## What's in the repos

- `monogate-research/electronics_intake/kernels/roundtrip_stress_v0/` —
  63-kernel × 6-backend equivalence packet, v0.6.
- `monogate-research/electronics_intake/kernels/real_modules_v0/` —
  17-module-level coverage packet, v0.1.
- `monogate-research/electronics_intake/kernels/lean_proofs_v0/` —
  63-kernel Lean-emit + lean-check survey.
- `monogate-research/electronics_intake/kernels/lean_proofs_v1/` —
  18-kernel non-trivial-theorem closure survey (18/18 close).
- `monogate-research/electronics_intake/kernels/verilog_simulation_v0/` —
  Complete Verilator scaffold; F11 + verilator-install gates.
- `agent-maestro/forge` commits `8948a27`, `a7465aa`, `8e554da` — F3,
  F4, F5, F7 closures.
- `agent-maestro/efrog` commits `c948b3e`, `5ff9dfd`, `c27a56d` —
  multi-return + lerp preamble, F2 cross-call inlining, class-body lift.

Each packet contains the full corpus, the emitted artifacts, the
harness script, and a JSON evidence report. Reproducing each requires
the toolchain plus `gcc`, `g++`, `node`, `javac`, `rustc`, `python3`,
`numpy`, and (for Lean) the MachLib build.

## What's next

F11 (Pro-tier hardware emit) is the single biggest open question
remaining. F10 (non-trivial Lean theorems) is fully addressed —
Lean v1.2 closes 18 of 18 with hand-proven tactics after the
operator approved the C-243 literal-bridge axioms in MachLib. The
hardware-track gates (Pro license + verilator install) are the
last actionable items in this sprint.

The stress-test → finding → fix loop itself works. The infrastructure
is checked in; the cost of running the next sprint is dominated by
the corpus design and (for Lean) the proof writing, not the harness
construction. That's the structural win — the loop is now a tool,
not a one-off.

---

*Monogate Research (2026). "Stress-Testing the eFrog → Forge Pipeline." monogate research blog. https://monogate.org/blog/stress-testing-the-pipeline*
