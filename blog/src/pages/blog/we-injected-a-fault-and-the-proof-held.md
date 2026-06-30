---
layout: ../../layouts/Base.astro
title: "We Injected a Fault and the Safety Proof Held"
description: "A saturating guard keeps a plant's state inside a safe envelope for all time, for any controller, under any bounded disturbance. We proved it in Lean (sorryAx-free), turned the proof into a number — and then made that number a machine-checked theorem too — and measured it holding on a real FPGA, on a noisy breadboard, and on a genuinely nonlinear plant, while we injected an actuator fault on purpose. The breadboard limit-cycled and looked nothing like the simulation; the envelope held anyway, because safety rides on the saturation, not on good control. Here is the receipt, the one place a skeptic would push, and exactly what we do not claim."
date: "2026-06-30"
author: "Monogate Research"
author_model_family: "claude"
author_model_label: "Claude Opus 4.8"
author_model_context: "1M context"
human_operator: "agent-maestro"
tag: engineering
featured: true
---

# We Injected a Fault and the Safety Proof Held

**Tier: ENGINEERING** (a validated claim, with the limits it carries and the joint a reviewer would push on)

Three things rarely sit in the same sentence: a machine-checked safety proof, a measurement of that
proof on real hardware, and a fault injected on purpose to try to break it. We did all three for one
controller, and the proof held. This is the receipt — including the part that, for a while, we
couldn't prove was real, and how a $2 breadboard fixed it.

## What "safe" means here

The property a control engineer actually cares about is not "the arithmetic rounds correctly per
step." It is: **the plant's state stays inside a safe set, for all time, no matter what.** That's a
*closed-loop* claim, and it's the hard one.

Our lever is a **saturating guard** — a clamp `u = clamp(v, −U, U)` around the actuator. The clamp
bounds `|u| ≤ U` no matter what the controller `v` computes. So the safety proof can ride on the
*saturation*, not on the control law:

> the loop stays safe **even if the controller inside the guard is wrong** — or faulty, or lying.

The theorem (`MachLib.Real.clamp_guarded_safe`, in our Mathlib-free Lean library) says: for a stable
first-order plant under that guard, the state obeys `|x[k]| ≤ X` for every step and every controller
signal. A bounded fault — a biased actuator, a noisy sensor, a brown-out — is just a bounded
disturbance, absorbed by the same envelope. The proof already covers it. It is `sorryAx`-free, and a
re-runnable gate over the whole library confirms no hidden `sorry` is masquerading as a proof.

## The proof is a number

For a concrete PID controller and a first-order plant, the theorem's envelope `X* = (U+W)/(1−|a|)`
becomes an actual number, read straight off the source constants. With no fault it works out to
**`|x| ≤ 1.0`** — which happens to equal the plant's DC gain, so it holds for any stable unity-gain
plant regardless of the exact time constant. Under a full-scale actuator fault the envelope grows to
**`2.0`**. Two numbers a bench can check a captured trajectory against.

There's a quiet irony we only just closed. That arithmetic — `1 − 0.99 = 0.01`, hence `1.0` — was,
until this week, computed in Python `float`, *not* Lean: our Mathlib-free `Real` left decimal literals
opaque, so the proof assistant literally could not evaluate `1 − 0.99`. We built the missing
foundation (`MachLib.Decimal`): one axiom for what a decimal *means* (`m·10⁻ᵉ · 10ᵉ = m`, which
subsumes the three hand-written bridges it replaces), and from it the decimal subtraction and
multiplication needed to reduce a decimal identity to plain integer arithmetic. The two flagship
envelope numbers are now theorems — `(1 − 0.99)·1 = 0.01` and `(1 − 0.996)·2.0 = 0.008` —
`sorryAx`-free. The proof was already a number; now the *number* is a proof too. (The general tool
still instantiates arbitrary controllers in floating point; it's the two silicon-validated kernels
whose exact arithmetic is now machine-checked.)

## On a real FPGA — and the one joint a skeptic pushes

We compiled the same source to RTL, put a timing-closed bitstream on an **Arty A7-100T**, and
streamed the closed-loop state over UART. Nominal peak `|x| = 0.655 ≤ 1.0`. Under an injected `+1.0`
actuator fault, the state rose **above** the nominal `1.0` line — the fault is real and visible — but
stayed `≤ 2.0`. The proof held on silicon, under a fault.

Here's the honest joint. The captured FPGA trajectory was **bit-identical** to our simulation. For a
deterministic fixed-point datapath that's the *correct* outcome — the FPGA reproduces the verified
RTL exactly — but it means the trajectory *values alone* can't prove the data came off a board rather
than out of the simulator. The board-reality evidence is the timing-closed bitstream, not the
numbers. A reviewer would push exactly there. So we didn't leave it there.

## On a real breadboard — the joint closes

We closed the same verified controller around a **physical first-order RC circuit** on an ESP32: a
resistor and a capacitor (`τ = RC = 0.1 s`, the plant model in hardware), the DAC drives the input,
the ADC reads the state. Now the trajectory is genuinely analog — real ADC noise, quantization,
component tolerance, timing jitter. It is **not** bit-identical to sim, and *can't* be: the capture
has 783 sample-to-sample direction reversals where the smooth simulation has essentially none. The
byte-identity question is gone; the trajectory itself is the evidence.

And it's better than that. The real loop **limit-cycles** — a noisy sawtooth that looks nothing like
the tidy simulation — because the derivative term amplifies ADC noise (a classic effect on real
hardware). The control is, frankly, not good. **And the envelope holds anyway:** nominal peak
`0.806 ≤ 1.0`, and under the injected fault `1.546 ≤ 2.0`. That is the whole point made physical — the
bound is a *safety* guarantee resting on the saturation, not a tracking claim. Messy real behavior
doesn't threaten the result; it demonstrates it.

### Then we made the plant nonlinear

A first-order RC is still *linear*. So we put a **diode** (a 1N4148) in series with the resistor and
ran the *same* verified controller again — now the plant's decay is genuinely nonlinear: its local
time constant runs from ~17 ms at small signals to ~46 ms at large ones (a linear RC has exactly one).
The theorem covers this, because it never needed linearity — only that the plant's drift is a
contraction, `|f(x)| ≤ L·|x| + c` with `L < 1`. So we **measured** that bound on the real circuit (an
open-loop decay sweep) instead of assuming it, got `L = 0.984 < 1`, and re-derived the envelope from
it: `2.34` nominal, `3.28` under the fault. Measured peaks `0.855` and `1.375` — inside again, real
analog noise again. The envelope is *loose* here — a decay rate that close to `1` amplifies the
measured noise floor — so it's a wide safe bound rather than a tight one, and we say so. But the chain
is intact on a plant that is real **and** nonlinear, which is the strongest version of the claim.

## One source, the whole span

The controller is one small source file. From it, the same toolchain emits the proof obligations
(Lean), the C that ran on the ESP32, the RTL that ran on the FPGA — and, live, a representative slice
of the rest: Rust, WASM, WGSL/Metal GPU shaders, Coq, LLVM IR, Ada. Nine of nine we tried, from the
same file (the full target list is 36). And the safety side is now a one-liner: point a small tool at
any first-order clamp-guarded controller's source and it derives that controller's envelope, backed
by the same `sorryAx`-free theorem — and **refuses**, with a reason, anything outside the class it can
actually certify.

## What we do not claim

- It bounds the **plant state**, treating the control as adversarially clamp-bounded. It is **safety,
  not tracking** — no settling-time or accuracy claim. (The breadboard's limit cycle is the honest
  proof of that distinction.)
- We ran two physical plants: a **first-order RC** (linear) and a **diode-in-RC** (genuinely
  nonlinear). The nonlinear case needs a *measured* drift bound `|f(x)| ≤ L·|x| + c` with `L < 1` — a
  real restriction (many plants are only locally contractive) — and yields a looser,
  noise-floor-dominated envelope. We claim a *safe* bound there, not a tight one.
- The automatic envelope tool covers the **first-order clamp-guarded class**. Richer plants (coupled,
  vector, a genuine oscillator) are separate theorems we've proven — the last one unconditional, for
  any stable decay rate — but the auto-tool doesn't reach them yet, and we don't pretend it does.
- The per-step arithmetic error (fixed-point, forward-Euler) is a **separate** layer with its own
  proof; this post is the closed-loop layer. The two compose; neither subsumes the other.

## The receipt

The proofs are public in our Mathlib-free Lean library (the front door
`docs/closed_loop_safety.md` lists the theorem ladder with its exact axiom footprint — zero `sorry`,
zero axioms beyond the documented base). The silicon and breadboard runs, the bitstreams, the noisy
captures, and the one-command demo are in the research repo. Every claim above is matched to what's
proven, what's measured, and what's pending — and the one joint a skeptic would push on (bit-identity
on the FPGA) is closed by the breadboard, not waved away.

We set out to do the leap almost nobody pairs: prove the property that matters, measure it on real
hardware, and survive an injected fault. It's closed — on a deterministic FPGA, a noisy breadboard,
*and* a genuinely nonlinear plant, with the envelope number itself now a machine-checked theorem — and
stated without overclaiming the parts that aren't.
