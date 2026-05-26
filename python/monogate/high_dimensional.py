"""High-dimensional geometry probes for EML tree space.

These helpers turn the "corners rule high-dimensional geometry" intuition into
small reproducible measurements that can be used by Forge/IR research without
pulling in NumPy or plotting dependencies.
"""

from __future__ import annotations

import json
import math
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class DepthProbe:
    depth: int
    leaf_dimension: int
    samples: int
    hypersphere_cube_ratio: float
    boundary_shell_fraction: float
    middle_ball_fraction: float
    raw_domain_valid_fraction: float
    positive_finite_fraction: float
    positive_non_saturated_fraction: float
    useful_volume_proxy: float


@dataclass(frozen=True)
class OptimizerTrace:
    regime: str
    depth: int
    leaf_dimension: int
    target: float
    seed: int
    steps: int
    final_label: str
    final_output: float | None
    final_loss: float | None
    best_loss: float | None
    domain_failures: int
    overflow_events: int
    saturation_events: int
    boundary_hits: int
    finite_steps: int
    terminal_boundary_fraction: float
    terminal_min: float
    terminal_max: float


TARGETS = {
    "zero": 0.0,
    "one": 1.0,
    "sqrt2": math.sqrt(2.0),
    "e": math.e,
    "pi": math.pi,
}


def hypersphere_cube_ratio(dimension: int) -> float:
    """Return V(unit d-ball) / V([-1, 1]^d)."""
    if dimension < 1:
        raise ValueError("dimension must be >= 1")
    log_ratio = (dimension / 2) * math.log(math.pi) - dimension * math.log(2) - math.lgamma(dimension / 2 + 1)
    return math.exp(log_ratio)


def boundary_shell_fraction(points: Iterable[list[float]], epsilon: float = 0.05) -> float:
    rows = list(points)
    if not rows:
        return 0.0
    return sum(max(abs(x) for x in row) >= 1 - epsilon for row in rows) / len(rows)


def middle_ball_fraction(points: Iterable[list[float]], radius_fraction: float = 0.5) -> float:
    rows = list(points)
    if not rows:
        return 0.0
    hits = 0
    for row in rows:
        radius = math.sqrt(sum(x * x for x in row))
        if radius <= radius_fraction * math.sqrt(len(row)):
            hits += 1
    return hits / len(rows)


def eval_full_eml_tree(leaves: list[float], domain_epsilon: float = 1e-12) -> float:
    """Evaluate a complete binary EML tree over a leaf vector.

    Raises ValueError when a right child leaves the log domain and OverflowError
    when exp() overflows. This intentionally models the brittle raw EML training
    surface before domain-aware Forge guards.
    """
    level = list(leaves)
    if not level or len(level) & (len(level) - 1):
        raise ValueError("leaf count must be a power of two")
    while len(level) > 1:
        nxt: list[float] = []
        for i in range(0, len(level), 2):
            x = level[i]
            y = level[i + 1]
            if y <= domain_epsilon:
                raise ValueError("right child outside log domain")
            value = math.exp(x) - math.log(y)
            if not math.isfinite(value):
                raise OverflowError("non-finite EML value")
            nxt.append(value)
        level = nxt
    return level[0]


def _eval_guarded_eml_tree(
    leaves: list[float],
    *,
    clamp_domain: bool = False,
    clamp_exp: bool = False,
    domain_epsilon: float = 1e-9,
) -> tuple[float | None, str | None]:
    level = list(leaves)
    try:
        while len(level) > 1:
            nxt: list[float] = []
            for i in range(0, len(level), 2):
                x = level[i]
                y = level[i + 1]
                if clamp_domain:
                    y = max(y, domain_epsilon)
                elif y <= domain_epsilon:
                    return None, "domain_failed"
                if clamp_exp:
                    x = max(min(x, 20.0), -20.0)
                value = math.exp(x) - math.log(y)
                if not math.isfinite(value):
                    return None, "overflowed"
                nxt.append(value)
            level = nxt
        return level[0], None
    except OverflowError:
        return None, "overflowed"


def _terminal_stats(leaves: list[float], boundary_epsilon: float = 0.05) -> dict:
    return {
        "terminal_boundary_fraction": sum(abs(x) >= 1 - boundary_epsilon for x in leaves) / len(leaves),
        "terminal_min": min(leaves),
        "terminal_max": max(leaves),
    }


def _trace_loss(
    leaves: list[float],
    target: float,
    *,
    clamp_domain: bool,
    clamp_exp: bool,
    l2: float,
    boundary_penalty: float,
    saturation_penalty: float,
    saturation_limit: float,
) -> tuple[float, float | None, str | None]:
    output, event = _eval_guarded_eml_tree(leaves, clamp_domain=clamp_domain, clamp_exp=clamp_exp)
    if event:
        return 1e6 + sum(abs(x) for x in leaves), None, event
    assert output is not None
    try:
        loss = (output - target) ** 2
        loss += l2 * sum(x * x for x in leaves)
    except OverflowError:
        return 1e12, output, "overflowed"
    if boundary_penalty:
        loss += boundary_penalty * sum(max(0.0, abs(x) - 0.90) ** 2 for x in leaves)
    if saturation_penalty and abs(output) > saturation_limit:
        try:
            loss += saturation_penalty * (abs(output) - saturation_limit) ** 2
        except OverflowError:
            return 1e12, output, "overflowed"
    if not math.isfinite(loss):
        return 1e12, output, "overflowed"
    return loss, output, None


def _finite_difference_gradient(
    leaves: list[float],
    target: float,
    *,
    clamp_domain: bool,
    clamp_exp: bool,
    l2: float,
    boundary_penalty: float,
    saturation_penalty: float,
    saturation_limit: float,
    eps: float = 1e-4,
) -> list[float]:
    grad: list[float] = []
    for i in range(len(leaves)):
        plus = list(leaves)
        minus = list(leaves)
        plus[i] += eps
        minus[i] -= eps
        lp, _, _ = _trace_loss(
            plus,
            target,
            clamp_domain=clamp_domain,
            clamp_exp=clamp_exp,
            l2=l2,
            boundary_penalty=boundary_penalty,
            saturation_penalty=saturation_penalty,
            saturation_limit=saturation_limit,
        )
        lm, _, _ = _trace_loss(
            minus,
            target,
            clamp_domain=clamp_domain,
            clamp_exp=clamp_exp,
            l2=l2,
            boundary_penalty=boundary_penalty,
            saturation_penalty=saturation_penalty,
            saturation_limit=saturation_limit,
        )
        g = (lp - lm) / (2 * eps)
        if not math.isfinite(g):
            g = 0.0
        grad.append(max(min(g, 100.0), -100.0))
    return grad


def run_optimizer_trace(
    *,
    regime: str,
    depth: int = 3,
    target: float = math.pi,
    seed: int = 20260526,
    steps: int = 80,
    learning_rate: float = 0.01,
    saturation_limit: float = 10.0,
) -> dict:
    """Run one small optimizer trace and return a replayable packet.

    Regimes are intentionally simple and dependency-free:
    `naive_gradient`, `regularized_gradient`, `guarded_gradient`,
    `boundary_aware_gradient`, and `random_search`.
    """
    rng = random.Random(seed)
    leaf_dimension = 2**depth
    positive_init = regime in {"guarded_gradient", "boundary_aware_gradient", "random_search"}
    leaves = [rng.uniform(0.1, 2.0) if positive_init else rng.uniform(-1.0, 1.0) for _ in range(leaf_dimension)]
    clamp_domain = regime in {"guarded_gradient", "boundary_aware_gradient"}
    clamp_exp = regime in {"guarded_gradient", "boundary_aware_gradient"}
    l2 = 1e-3 if regime in {"regularized_gradient", "boundary_aware_gradient"} else 0.0
    boundary_penalty = 0.05 if regime == "boundary_aware_gradient" else 0.0
    saturation_penalty = 0.05 if regime == "boundary_aware_gradient" else 0.0

    events = {"domain_failed": 0, "overflowed": 0, "saturated": 0, "boundary_hit": 0}
    frames = []
    best_loss = math.inf
    final_output: float | None = None
    final_loss: float | None = None
    finite_steps = 0

    for step in range(steps):
        if regime == "random_search":
            candidate = [rng.uniform(0.1, 2.0) for _ in range(leaf_dimension)]
            loss, output, event = _trace_loss(
                candidate,
                target,
                clamp_domain=False,
                clamp_exp=False,
                l2=0.0,
                boundary_penalty=0.0,
                saturation_penalty=0.0,
                saturation_limit=saturation_limit,
            )
            if loss < best_loss:
                leaves = candidate
        else:
            loss, output, event = _trace_loss(
                leaves,
                target,
                clamp_domain=clamp_domain,
                clamp_exp=clamp_exp,
                l2=l2,
                boundary_penalty=boundary_penalty,
                saturation_penalty=saturation_penalty,
                saturation_limit=saturation_limit,
            )

        if event:
            events[event] += 1
        else:
            finite_steps += 1
            final_output = output
            final_loss = loss
            best_loss = min(best_loss, loss)
            if output is not None and abs(output) > saturation_limit:
                events["saturated"] += 1

        stats = _terminal_stats(leaves)
        if stats["terminal_boundary_fraction"] > 0:
            events["boundary_hit"] += 1
        if step in {0, 1, 2, 4, 9, steps - 1}:
            frames.append(
                {
                    "step": step,
                    "loss": None if not math.isfinite(loss) else loss,
                    "output": output,
                    "event": event,
                    **stats,
                }
            )

        if regime != "random_search":
            grad = _finite_difference_gradient(
                leaves,
                target,
                clamp_domain=clamp_domain,
                clamp_exp=clamp_exp,
                l2=l2,
                boundary_penalty=boundary_penalty,
                saturation_penalty=saturation_penalty,
                saturation_limit=saturation_limit,
            )
            leaves = [x - learning_rate * g for x, g in zip(leaves, grad)]
            if regime == "boundary_aware_gradient":
                leaves = [max(min(x, 2.0), 0.05) for x in leaves]

    stats = _terminal_stats(leaves)
    if final_output is None:
        label = "domain_failed" if events["domain_failed"] >= events["overflowed"] else "overflowed"
    elif final_loss is not None and final_loss < 1e-4:
        label = "converged"
    elif events["saturated"] > steps / 3:
        label = "saturated"
    elif finite_steps < steps / 2:
        label = "collapsed"
    else:
        label = "transient"

    trace = OptimizerTrace(
        regime=regime,
        depth=depth,
        leaf_dimension=leaf_dimension,
        target=target,
        seed=seed,
        steps=steps,
        final_label=label,
        final_output=final_output,
        final_loss=final_loss,
        best_loss=None if not math.isfinite(best_loss) else best_loss,
        domain_failures=events["domain_failed"],
        overflow_events=events["overflowed"],
        saturation_events=events["saturated"],
        boundary_hits=events["boundary_hit"],
        finite_steps=finite_steps,
        **stats,
    )
    return {
        "schema_version": "monogate.forge_attractor_trace.v1",
        "trace": asdict(trace),
        "frames": frames,
        "boundaries": {
            "sampled_evidence_only": True,
            "optimizer_release_claim": False,
            "phantom_attractor_proof": False,
            "hardware_claim": False,
        },
    }


def run_forge_attractor_trace_packet(
    *,
    depth: int = 3,
    target: float = math.pi,
    seed: int = 20260526,
    steps: int = 80,
) -> dict:
    regimes = [
        "naive_gradient",
        "regularized_gradient",
        "guarded_gradient",
        "boundary_aware_gradient",
        "random_search",
    ]
    traces = [
        run_optimizer_trace(regime=regime, depth=depth, target=target, seed=seed + index, steps=steps)
        for index, regime in enumerate(regimes)
    ]
    return {
        "schema_version": "monogate.forge_attractor_trace_packet.v1",
        "depth": depth,
        "leaf_dimension": 2**depth,
        "target": target,
        "seed": seed,
        "steps": steps,
        "regime_count": len(regimes),
        "traces": traces,
        "summary": [
            {
                "regime": item["trace"]["regime"],
                "label": item["trace"]["final_label"],
                "best_loss": item["trace"]["best_loss"],
                "domain_failures": item["trace"]["domain_failures"],
                "overflow_events": item["trace"]["overflow_events"],
                "saturation_events": item["trace"]["saturation_events"],
                "finite_steps": item["trace"]["finite_steps"],
            }
            for item in traces
        ],
        "machlib_lean_obligations": [
            "Prove V(unit_ball_d) / V([-1,1]^d) -> 0.",
            "Prove cube boundary-shell probability 1 - (1 - epsilon)^d -> 1.",
            "For independent symmetric leaves, prove raw right-child positivity probability decays exponentially by first EML layer.",
            "Connect guarded lowering packets to domain-preservation obligations.",
        ],
        "boundaries": {
            "sampled_evidence_only": True,
            "optimizer_release_claim": False,
            "phantom_attractor_proof": False,
            "formal_verification_claim": False,
            "hardware_claim": False,
        },
    }


def run_useful_volume_census(
    *,
    depths: Iterable[int] = range(1, 7),
    targets: dict[str, float] | None = None,
    samples: int = 2000,
    seed: int = 20260526,
    tolerance: float = 0.1,
    saturation_limit: float = 10.0,
) -> dict:
    """Estimate target-adjacent finite volume across EML tree depths."""
    rng = random.Random(seed)
    target_map = targets or TARGETS
    distributions = {
        "raw_cube": lambda n: [rng.uniform(-1.0, 1.0) for _ in range(n)],
        "positive_box": lambda n: [rng.uniform(0.1, 2.0) for _ in range(n)],
        "guarded_cube": lambda n: [rng.uniform(-1.0, 1.0) for _ in range(n)],
    }
    rows = []

    for depth in depths:
        leaf_dimension = 2**depth
        for distribution, sampler in distributions.items():
            for target_name, target_value in target_map.items():
                finite = 0
                non_saturated = 0
                target_adjacent = 0
                best_abs_error = math.inf
                for _ in range(samples):
                    leaves = sampler(leaf_dimension)
                    if distribution == "guarded_cube":
                        value, event = _eval_guarded_eml_tree(leaves, clamp_domain=True, clamp_exp=True)
                        if event:
                            continue
                    else:
                        try:
                            value = eval_full_eml_tree(leaves)
                        except (ValueError, OverflowError):
                            continue
                    if value is None or not math.isfinite(value):
                        continue
                    finite += 1
                    abs_error = abs(value - target_value)
                    best_abs_error = min(best_abs_error, abs_error)
                    if abs(value) <= saturation_limit:
                        non_saturated += 1
                        if abs_error <= tolerance:
                            target_adjacent += 1

                finite_fraction = finite / samples
                non_saturated_fraction = non_saturated / samples
                adjacent_fraction = target_adjacent / samples
                rows.append({
                    "depth": depth,
                    "leaf_dimension": leaf_dimension,
                    "distribution": distribution,
                    "target": target_name,
                    "target_value": target_value,
                    "samples": samples,
                    "finite_fraction": finite_fraction,
                    "non_saturated_fraction": non_saturated_fraction,
                    "target_adjacent_fraction": adjacent_fraction,
                    "useful_volume_ratio": adjacent_fraction,
                    "best_abs_error": None if not math.isfinite(best_abs_error) else best_abs_error,
                })

    return {
        "schema_version": "monogate.high_dim_useful_volume_census.v1",
        "seed": seed,
        "samples_per_case": samples,
        "tolerance": tolerance,
        "saturation_limit": saturation_limit,
        "targets": target_map,
        "rows": rows,
        "boundaries": {
            "sampled_evidence_only": True,
            "symbolic_usefulness_proof": False,
            "optimizer_release_claim": False,
            "hardware_claim": False,
        },
    }


def build_high_dim_formalization_bridge() -> dict:
    obligations = [
        {
            "id": "HD001_ball_cube_ratio_tends_zero",
            "status": "stub",
            "informal_statement": "The volume ratio V(unit_ball_d) / V([-1,1]^d) tends to zero as d tends to infinity.",
            "lean_name": "high_dim_ball_cube_ratio_tends_zero",
            "lean_statement": "theorem high_dim_ball_cube_ratio_tends_zero : Tendsto ballCubeRatio atTop (𝓝 0) := by",
            "depends_on": ["Gamma asymptotics", "volume formula for Euclidean balls"],
        },
        {
            "id": "HD002_cube_boundary_shell_tends_one",
            "status": "stub",
            "informal_statement": "For fixed epsilon in (0,1), the cube boundary-shell probability tends to one.",
            "lean_name": "cube_boundary_shell_probability_tends_one",
            "lean_statement": "theorem cube_boundary_shell_probability_tends_one (ε : Real) (hε : 0 < ε ∧ ε < 1) : Tendsto (fun d => 1 - (1 - ε)^d) atTop (𝓝 1) := by",
            "depends_on": ["geometric decay"],
        },
        {
            "id": "HD003_first_layer_log_domain_survival",
            "status": "stub",
            "informal_statement": "For independent symmetric terminal leaves, raw first-layer EML right-child log-domain survival decays exponentially.",
            "lean_name": "eml_first_layer_log_domain_survival_decay",
            "lean_statement": "theorem eml_first_layer_log_domain_survival_decay (d : Nat) : firstLayerSurvival d = (1 / 2 : Real) ^ (2 ^ (d - 1)) := by",
            "depends_on": ["independence of right children", "symmetric positivity probability"],
        },
        {
            "id": "HD004_guarded_lowering_domain_preservation",
            "status": "stub",
            "informal_statement": "Guarded EML lowering preserves declared positive-domain obligations through replay packets.",
            "lean_name": "guarded_lowering_preserves_domain_annotations",
            "lean_statement": "theorem guarded_lowering_preserves_domain_annotations (p : ReplayPacket) : ValidGuards p -> DomainPreserved p := by",
            "depends_on": ["EML IR replay schema", "domain annotation semantics"],
        },
    ]
    return {
        "schema_version": "monogate.high_dim_formalization_bridge.v1",
        "obligation_count": len(obligations),
        "obligations": obligations,
        "boundaries": {
            "theorem_stub_only": True,
            "formal_verification_claim": False,
            "mathlib_dependency_claim": False,
        },
    }


def run_corner_concentration_probe(
    *,
    depths: Iterable[int] = range(1, 8),
    samples: int = 2000,
    seed: int = 20260526,
    boundary_epsilon: float = 0.05,
    saturation_limit: float = 10.0,
) -> dict:
    """Sample full EML trees and return a public-safe research packet."""
    rng = random.Random(seed)
    rows: list[DepthProbe] = []

    for depth in depths:
        leaf_dimension = 2**depth
        raw_points = [[rng.uniform(-1.0, 1.0) for _ in range(leaf_dimension)] for _ in range(samples)]
        positive_points = [[rng.uniform(0.1, 2.0) for _ in range(leaf_dimension)] for _ in range(samples)]

        raw_valid = 0
        finite = 0
        non_saturated = 0
        for point in raw_points:
            try:
                eval_full_eml_tree(point)
                raw_valid += 1
            except (ValueError, OverflowError):
                pass

        for point in positive_points:
            try:
                value = eval_full_eml_tree(point)
            except (ValueError, OverflowError):
                continue
            finite += 1
            if abs(value) <= saturation_limit:
                non_saturated += 1

        finite_fraction = finite / samples
        non_saturated_fraction = non_saturated / samples
        rows.append(
            DepthProbe(
                depth=depth,
                leaf_dimension=leaf_dimension,
                samples=samples,
                hypersphere_cube_ratio=hypersphere_cube_ratio(leaf_dimension),
                boundary_shell_fraction=boundary_shell_fraction(raw_points, boundary_epsilon),
                middle_ball_fraction=middle_ball_fraction(raw_points),
                raw_domain_valid_fraction=raw_valid / samples,
                positive_finite_fraction=finite_fraction,
                positive_non_saturated_fraction=non_saturated_fraction,
                useful_volume_proxy=finite_fraction * non_saturated_fraction,
            )
        )

    return {
        "schema_version": "monogate.high_dim_corner_concentration.v1",
        "seed": seed,
        "samples_per_depth": samples,
        "boundary_epsilon": boundary_epsilon,
        "saturation_limit": saturation_limit,
        "interpretation": {
            "hypersphere_cube_ratio": "Analytic V(unit ball) / V([-1,1]^d).",
            "boundary_shell_fraction": "Sample fraction with at least one terminal coordinate within epsilon of a cube face.",
            "middle_ball_fraction": "Sample fraction inside radius 0.5*sqrt(d), a crude middle-of-cube proxy.",
            "raw_domain_valid_fraction": "Raw [-1,1] terminal vectors that evaluate without log-domain failure.",
            "positive_non_saturated_fraction": "Positive-domain terminal vectors that evaluate finite with |output| <= saturation_limit.",
            "useful_volume_proxy": "Finite positive-domain fraction times non-saturated fraction; not a proof of useful symbolic solutions.",
        },
        "rows": [asdict(row) for row in rows],
        "boundaries": {
            "sampled_evidence_only": True,
            "phantom_attractor_proof": False,
            "optimizer_release_claim": False,
            "hardware_claim": False,
        },
    }


def write_probe_outputs(packet: dict, output_json: Path, output_markdown: Path) -> None:
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_markdown.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# High-D Corner Concentration Probe",
        "",
        f"Schema: `{packet['schema_version']}`",
        f"Samples per depth: `{packet['samples_per_depth']}`",
        f"Seed: `{packet['seed']}`",
        "",
        "| depth | leaves | ball/cube | boundary shell | middle proxy | raw valid | positive finite | non-saturated | useful proxy |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in packet["rows"]:
        lines.append(
            "| {depth} | {leaf_dimension} | {hypersphere_cube_ratio:.3e} | "
            "{boundary_shell_fraction:.3f} | {middle_ball_fraction:.3f} | "
            "{raw_domain_valid_fraction:.3f} | {positive_finite_fraction:.3f} | "
            "{positive_non_saturated_fraction:.3f} | {useful_volume_proxy:.3f} |".format(**row)
        )
    lines.extend(
        [
            "",
            "This is sampled evidence only. It measures the geometry pressure that makes",
            "EML tree optimization brittle in high-dimensional terminal space; it does",
            "not prove a phantom-attractor theorem or make a hardware claim.",
            "",
        ]
    )
    output_markdown.write_text("\n".join(lines), encoding="utf-8")


def write_trace_outputs(packet: dict, output_json: Path, output_markdown: Path) -> None:
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_markdown.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Forge Attractor Trace Packet",
        "",
        f"Schema: `{packet['schema_version']}`",
        f"Depth: `{packet['depth']}`",
        f"Leaf dimension: `{packet['leaf_dimension']}`",
        f"Steps per regime: `{packet['steps']}`",
        "",
        "| regime | label | best loss | domain failures | overflow | saturation | finite steps |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in packet["summary"]:
        best = row["best_loss"]
        best_text = "n/a" if best is None else f"{best:.3e}"
        lines.append(
            f"| {row['regime']} | {row['label']} | {best_text} | "
            f"{row['domain_failures']} | {row['overflow_events']} | "
            f"{row['saturation_events']} | {row['finite_steps']} |"
        )
    lines.extend(["", "## MachLib / Lean Obligations", ""])
    for item in packet["machlib_lean_obligations"]:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "This packet compares optimizer regimes against the same high-dimensional",
            "EML terminal geometry. It is sampled evidence only and does not claim a",
            "phantom-attractor theorem, optimizer release, hardware result, or formal",
            "verification.",
            "",
        ]
    )
    output_markdown.write_text("\n".join(lines), encoding="utf-8")


def write_useful_volume_outputs(packet: dict, output_json: Path, output_markdown: Path) -> None:
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_markdown.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# High-D Useful Volume Census",
        "",
        f"Schema: `{packet['schema_version']}`",
        f"Samples per case: `{packet['samples_per_case']}`",
        f"Tolerance: `{packet['tolerance']}`",
        "",
        "| depth | distribution | target | finite | non-saturated | target-adjacent | best abs error |",
        "|---:|---|---|---:|---:|---:|---:|",
    ]
    for row in packet["rows"]:
        best = row["best_abs_error"]
        best_text = "n/a" if best is None else f"{best:.3e}"
        lines.append(
            f"| {row['depth']} | {row['distribution']} | {row['target']} | "
            f"{row['finite_fraction']:.3f} | {row['non_saturated_fraction']:.3f} | "
            f"{row['target_adjacent_fraction']:.4f} | {best_text} |"
        )
    lines.extend([
        "",
        "Target-adjacent volume is sampled evidence only. It is a useful frontier",
        "signal for Forge heuristics, not a proof of symbolic reachability.",
        "",
    ])
    output_markdown.write_text("\n".join(lines), encoding="utf-8")


def write_formalization_bridge_outputs(packet: dict, output_json: Path, output_markdown: Path) -> None:
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_markdown.parent.mkdir(parents=True, exist_ok=True)
    output_json.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
    lines = ["# High-D Formalization Bridge", "", f"Schema: `{packet['schema_version']}`", ""]
    for item in packet["obligations"]:
        lines.extend([
            f"## {item['id']}",
            "",
            f"Status: `{item['status']}`",
            "",
            item["informal_statement"],
            "",
            "```lean",
            item["lean_statement"],
            "  sorry",
            "```",
            "",
        ])
    lines.append("These are theorem stubs, not completed formal proofs.")
    output_markdown.write_text("\n".join(lines), encoding="utf-8")
