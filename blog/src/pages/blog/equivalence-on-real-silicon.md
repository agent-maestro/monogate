---
layout: ../../layouts/Base.astro
title: "We Put the Proof on a Real FPGA"
description: "One verified math source compiles to software, RTL, and a GPU shader. We stopped trusting the model and ran each artifact for real — C on gcc, RTL in Verilator, a shader on an NVIDIA GPU, and the datapath on an Arty A7 FPGA — checking every output against a Lean-proved error bound. Each one held. Building it found six real bugs. Here is the receipt, and here is exactly where it doesn't hold."
date: "2026-06-29"
author: "Monogate Research"
tag: engineering
---

# We Put the Proof on a Real FPGA

**Tier: ENGINEERING** (a validated claim, with the failures it surfaced and the limits it carries)

The pitch for a multi-target compiler writes itself: one source, many backends, *provably* the same number everywhere. The pitch is also where most such projects quietly overclaim — "cross-target equivalence" usually means a model agreeing with another model.

So we did the un-fun thing. We took a forward-error bound proved in Lean, and instead of comparing the compiler's *model* of each target, we **ran the actual emitted artifact** — the gcc-compiled binary, the Verilator-simulated RTL, the WGSL shader on a real GPU, and the datapath on a physical FPGA — and checked the real output against the proved bound, sample by sample.

This post is the result. It includes a receipt you could reproduce, the six bugs the process found, and a plain statement of where the bound does **not** hold.

## What is actually proved

The certifier is a [Lean](/proofs) fold over a small operator basis. For any kernel built from it, one structural induction (`gexpr_sound`) yields a forward-error bound `E` such that the computed value is within `E` of the exact real value, at a stated per-operation rounding budget. A separate fold (`fx_sound`) does the same for the **fixed-point** (RTL) datapath, where each operation truncates onto a Q-format grid.

Both are `sorryAx`-free — `#print axioms` shows only the model's own primitives, no holes. The bound is not asserted; it is a theorem.

The link from "what we proved" to "what we ship" is a content hash of the kernel's syntax tree (`tree_hash`). If the source drifts, the hash changes and the binding is flagged — the proof is pinned to the exact expression that compiles.

## The receipt

The canonical kernel is a PID controller — `clamp(Kp·e + Ki·i + Kd·d, −1, 1)`. One EML source. Here is the certificate our tooling emits, every line a measured run of the real artifact against the proved bound `Ebound`:

```
EQUIVALENCE CERTIFICATE — pid
tree_hash : sha256:c163ea90…
proof     : float gexpr_sound ✓   fixed-point fx_sound ✓   (sorryAx-free)
binding   : AST tree_hash pins proof → shipped source
──────────────────────────────────────────────────────────────
real C   (f64, gcc -O2)        max|out−exact| = 2.44e-16 ≤ Ebound 8.69e-16  ✓
real RTL (Q16.16, Verilator)   max|out−exact| = 6.27e-05 ≤ Ebound 7.63e-05  ✓
real GPU (f32, wgpu/Vulkan)    max|out−exact| = 1.31e-07 ≤ Ebound 3.98e-07  ✓
real FPGA (Q16.16, Arty A7)    max|out−exact| = 4.05 LSB ≤ 5.0 LSB proven   ✓
```

The reference at each row is a 50-digit `mpmath` evaluation, not another float. The FPGA row is a 256-vector sweep of the synthesized datapath on a Digilent Arty A7-100T, captured over UART and checked against the same fixed-point bound — `0` violations. The simulated RTL (6.27e-5) and the real silicon (6.18e-5 raw) agree almost exactly, and both sit inside the bound the Lean fold proves.

Across the wider standard library, the same machinery runs **306 kernels through gcc-compiled C (≈15k samples, 0 violations)** and **306 through a real GPU (≈61k samples, 0 violations)**, each within the bound at that target's precision.

## The part that earns trust: it kept finding bugs

A green checkmark proves nothing if the harness can't go red. Every time we pointed a real-artifact lane at the corpus for the first time, it caught something a *model* would have missed:

1. **A clamp the proof didn't actually cover.** `clamp(x, alpha·x, hi)` blew the bound — at *zero* drift from the float reference, so the bound itself was wrong. The certifier's clamp assumed exact edges; `alpha·x` is rounded. We proved the joint-Lipschitz fix (`clampO3`) and re-validated.
2. **GPU division is not correctly-rounded.** A kernel with one division exceeded the bound on the GPU; the GB10's f32 divide measured **1.72 ulp** off true (Vulkan only guarantees ~2.5 ulp). The per-operation budget now reflects that.
3. **GPU `log` can't be relative-bounded.** The device's fast-math `log` carries an *absolute* error — **90 ulp near x = 1**, where the true value is ≈ 0. No finite relative budget encloses that, so log-using kernels are *excluded* from the GPU claim, with the measurement as the stated reason.
4. **A fixed-point overflow trick.** A `sign` kernel used `x · 1e30` to saturate; in Q16.16 that intermediate overflows and the 32-bit multiply *wraps* on real RTL. Not realizable in the format — honestly skipped.
5. **A sign-decode bug in our own RTL harness** (negative Q16.16 outputs read as unsigned), and **two Verilog-backend defects** that stopped the FPGA build cold (a dropped named constant; an un-encoded refinement guard).
6. **The "4-stage pipeline" that wasn't.** The emitted RTL collapsed to one register, so the multiply-add missed 100 MHz timing. The multipliers are now registered; the numeric result is identical (Verilator-confirmed).

We publish these because the failures are the evidence. A tool that finds and states its own limits is worth more than one that only ever shows green.

## Where it does *not* hold

In the same spirit:

- **Off the basis, there is no claim.** Anything outside the supported operators (general control flow, loops, `floor`, data-dependent guards beyond the modeled ones) is not certified — it is reported as off-basis, not silently passed.
- **GPU transcendentals near their zeros** (`log` at 1, `sin`/`cos` at multiples of π) are not relative-bounded; we exclude the operators that fail in the sampled domain rather than pretend a budget covers them.
- **Timing closure is board-confirmed, not proved here.** We validate the *numeric* result on silicon; that the design meets 100 MHz is a synthesis fact the bench checks, not something the Lean proof says.
- **The bound is an upper bound.** On PID the real silicon used ~4 LSB against a ~5 LSB proven bound — honest headroom, not a tight equality.
- **This is research and craft.** It is one verified kernel walked end-to-end, plus a corpus sweep — not a certified product, and we make no safety or qualification claims.

## What this is, and what it isn't

It is *not* a moat on any single target. High-level synthesis (Vitis, Bambu), verified compilation (CompCert, Fiat-Crypto), and multi-target DSLs (Halide, SPIRAL) are each mature and, target for target, ahead of us.

What is unusual is the **span checked on the real artifact**: one proved source whose error bound we *measured* holding on a real binary, real simulated RTL, a real GPU, and real FPGA silicon — and which, at every link, told us exactly where it breaks. We would rather underclaim against something checkable than overclaim against a model.

## The theory underneath, briefly

For the inner-product kernels (PID's `Kp·e + Ki·i + Kd·d` is one), the certifier now also proves the two companion lenses numerical analysts actually trust:

- **backward stability** — the computed output is the *exact* output of slightly-perturbed inputs (mistuned gains), within `(1+w)ⁿ − 1`;
- **the condition number** — when no catastrophic cancellation occurs, the relative forward error is `≤ 3·γ`, i.e. Higham's `forward ≲ κ · backward`, now proved at every arity.

Forward error, backward error, and conditioning — three views of the same rounding — meet in one place, `sorryAx`-free.

---

*The certifier and its real-artifact probes live in the Monogate toolchain; the proofs are in [MachLib](https://github.com/agent-maestro/machlib). If you find a kernel where the measured error beats — or breaks — the bound, that is exactly the report we want.*
