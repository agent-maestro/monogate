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

Five evidence packets, each producing a JSON report and a checked-in
artifact set.

| Packet | Question | Result |
|---|---|---|
| `roundtrip_stress_v0.6` | Do 63 single-purpose math kernels emit numerically-equivalent code across 6 software backends? | **63/63 ok on every backend, 0 drift flags.** |
| `real_modules_v0.1`     | Do 17 multi-function modules lift end-to-end through eFrog and compile through Forge? | **15/17 lift; the 2 fails are documented coverage deferrals.** |
| `lean_proofs_v0`        | Does Forge's Lean target produce code that lean-checks under MachLib? | **63/63 emit + lean-check pass under MachLib.** |
| `verilog_simulation_v0` | Same question but Verilator behavioural simulation. | **Scaffold-only — F11 blocks survey on Pro-tier license.** |
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
explicit `@verify(lean, theorem="...")` block (F9). The harness
worked around this with a programmatic verify prelude. Without
`requires`/`ensures` clauses, the emitted theorems are tautologies
(`True := by trivial`) — closing non-trivial theorems is the v1
follow-up (F10).

**F11 — Hardware targets Pro-tier locked**

All four Forge hardware targets (`verilog`, `systemverilog`, `vhdl`,
`chisel`) refuse on the Free tier. This is the first finding in the
sprint where the gate is **licensing**, not code. The harness
scaffold is checked in and runs end-to-end the moment the gate
opens. F11 is the single largest open-question of the sprint and the
direct test of the "Forge → FPGA" product claim — without it,
the hardware story stays asserted but not independently verified.

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
- `monogate-research/electronics_intake/kernels/verilog_simulation_v0/` —
  Scaffold; F11 finding.
- `agent-maestro/forge` commits `8948a27`, `a7465aa`, `8e554da` — F3,
  F4, F5, F7 closures.
- `agent-maestro/efrog` commits `c948b3e`, `5ff9dfd`, `c27a56d` —
  multi-return + lerp preamble, F2 cross-call inlining, class-body lift.

Each packet contains the full corpus, the emitted artifacts, the
harness script, and a JSON evidence report. Reproducing each requires
the toolchain plus `gcc`, `g++`, `node`, `javac`, `rustc`, `python3`,
`numpy`, and (for Lean) the MachLib build.

## What's next

F11 (Pro-tier hardware emit) is the single biggest open question. F10
(non-trivial Lean theorems) is the next-largest. Both are downstream
of the same engineering pipeline; the only thing missing is either a
license activation or a corpus augmentation pass.

The stress-test → finding → fix loop itself works. The infrastructure
is checked in; the cost of running the next sprint is dominated by
the corpus design, not the harness construction. That's the structural
win — the loop is now a tool, not a one-off.

---

*Monogate Research (2026). "Stress-Testing the eFrog → Forge Pipeline." monogate research blog. https://monogate.org/blog/stress-testing-the-pipeline*
