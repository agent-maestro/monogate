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
