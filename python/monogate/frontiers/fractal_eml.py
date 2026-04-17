"""
fractal_eml.py — EML Complexity of Fractal Geometry.

Session 52 findings:
  - Iterated Function Systems (IFS): affine maps are EML-1 per step;
    the ATTRACTOR (limit set) is EML-inf (dense fractal structure).
  - Koch snowflake: EML-2 per iteration step (rotation + scale),
    but the limit curve is EML-inf (infinite detail).
  - Sierpinski triangle: EML-1 per IFS step (scaling + translation).
  - Mandelbrot set: z_{n+1} = z_n² + c is EML-2 per iterate.
    Membership test is a LIMIT — EML-inf (the boundary is infinitely complex).
  - Julia sets: same map as Mandelbrot at fixed c; similar EML analysis.
  - Fractal dimension: Hausdorff dimension d_H is computable but the
    GEOMETRY is EML-inf because self-similar detail never terminates.

Key insight:
  Fractal = EML-finite iteration + EML-inf limit.
  The MAP is EML-finite; the ATTRACTOR is EML-inf.
  This is the fractal analogue of: "sin is EML-3 but noise is EML-inf."
  (The iteration is analytic; the infinite repetition is not.)
"""

from __future__ import annotations

import math
import cmath
from dataclasses import dataclass
from typing import Callable

import numpy as np

__all__ = [
    "IFSSystem",
    "SierpinskiIFS",
    "KochCurve",
    "MandelbrotSet",
    "JuliaSet",
    "FRACTAL_TAXONOMY",
    "analyze_fractal_eml",
    "fractal_taxonomy_table",
]


# ── IFS Base ──────────────────────────────────────────────────────────────────

@dataclass
class IFSSystem:
    """
    Iterated Function System: attractor = fixed point of union of affine maps.
    w_i(x) = A_i * x + b_i  (A_i: 2×2 matrix, b_i: translation)

    EML analysis:
      Each affine map w_i is EML-1 (linear).
      One IFS step (pick random w_i, apply) is EML-1.
      Attractor = limit set after inf iterations = EML-inf.
    """
    name: str
    maps: list[Callable[[np.ndarray], np.ndarray]]
    n_maps: int
    contraction_ratio: float
    hausdorff_dim: float
    eml_per_step: int = 1

    def random_iterate(self, x0: np.ndarray, n_steps: int = 50000) -> np.ndarray:
        """Chaos game: random IFS iteration."""
        rng = np.random.default_rng(42)
        pts = np.empty((n_steps, 2))
        x = x0.copy()
        for i in range(n_steps):
            idx = rng.integers(0, self.n_maps)
            x = self.maps[idx](x)
            pts[i] = x
        return pts

    def eml_analysis(self) -> dict[str, object]:
        return {
            "name": self.name,
            "eml_per_step": self.eml_per_step,
            "eml_attractor": "inf",
            "n_maps": self.n_maps,
            "contraction_ratio": self.contraction_ratio,
            "hausdorff_dim": self.hausdorff_dim,
            "insight": (
                f"IFS '{self.name}': {self.n_maps} affine maps, each EML-{self.eml_per_step}. "
                f"Attractor has Hausdorff dim={self.hausdorff_dim:.4f}. "
                "The MAP is EML-1 per step; the LIMIT SET is EML-inf (fractal). "
                "Self-similarity requires infinitely many compositions."
            ),
        }


class SierpinskiIFS(IFSSystem):
    """Sierpinski triangle via IFS: 3 maps, each scales by 1/2."""

    def __init__(self) -> None:
        # Three affine contractions: scale 1/2, translate to each vertex
        maps = [
            lambda x: 0.5 * x,
            lambda x: 0.5 * x + np.array([0.5, 0.0]),
            lambda x: 0.5 * x + np.array([0.25, 0.5 * math.sqrt(3) / 2]),
        ]
        super().__init__(
            name="sierpinski_triangle",
            maps=maps,
            n_maps=3,
            contraction_ratio=0.5,
            hausdorff_dim=math.log(3) / math.log(2),  # log3/log2 ≈ 1.585
            eml_per_step=1,
        )


# ── Koch Curve ────────────────────────────────────────────────────────────────

class KochCurve:
    """
    Koch snowflake via subdivision.

    At each step, replace each line segment with 4 segments:
      - Scale by 1/3
      - Rotate middle segment by ±60°

    EML per iteration step:
      Rotation by 60°: cos(60°) = 0.5 (exact), sin(60°) = √3/2 (EML-2).
      Scale + rotate + translate: EML-2 (matrix-vector multiply with trig constants).
    EML attractor: inf (fractal boundary).
    """

    def __init__(self) -> None:
        self.hausdorff_dim = math.log(4) / math.log(3)  # ≈ 1.262

    def iterate(self, points: list[complex], n_steps: int = 4) -> list[complex]:
        """Apply n_steps Koch subdivision iterations."""
        for _ in range(n_steps):
            points = self._subdivide(points)
        return points

    def _subdivide(self, pts: list[complex]) -> list[complex]:
        new_pts = []
        for i in range(len(pts) - 1):
            a, b = pts[i], pts[i + 1]
            p1 = a + (b - a) / 3.0
            p2 = a + (b - a) * complex(0.5, math.sqrt(3) / 6.0)  # rotate 60°
            p3 = a + 2.0 * (b - a) / 3.0
            new_pts.extend([a, p1, p2, p3])
        new_pts.append(pts[-1])
        return new_pts

    def eml_analysis(self) -> dict[str, object]:
        return {
            "name": "koch_curve",
            "eml_per_step": 2,
            "eml_attractor": "inf",
            "hausdorff_dim": self.hausdorff_dim,
            "n_segments_at_step_n": "4^n",
            "insight": (
                "Koch subdivision: each segment becomes 4 via scale(1/3) + rotate(60°). "
                "Rotation uses cos(60°)=0.5 (exact), sin(60°)=√3/2 (irrational constant). "
                "Full step is EML-2 (scale·complex multiply = degree-2 poly in Re/Im). "
                "Limit curve: 4^n segments → ∞. EML-inf limit (infinite self-similar detail). "
                f"Hausdorff dim = log(4)/log(3) ≈ {self.hausdorff_dim:.4f}."
            ),
        }

    def segment_count(self, n_steps: int) -> int:
        return 3 * (4 ** n_steps)


# ── Mandelbrot Set ────────────────────────────────────────────────────────────

class MandelbrotSet:
    """
    Mandelbrot set: c in M iff z_{n+1} = z_n² + c does not diverge.
    z_0 = 0.

    z_{n+1} = z_n² + c: squaring a complex number.
    In (Re,Im) coordinates: (x,y) -> (x²-y²+Re(c), 2xy+Im(c))
    This is EXACTLY degree-2 polynomial in (x,y) → EML-2 per step.

    The Mandelbrot set boundary is EML-inf:
      - It is NOT a real-analytic curve (fractal, non-rectifiable)
      - Membership test requires inf iterations (limit test)
      - The boundary has Hausdorff dim = 2 (Shishikura 1998)
    """

    def __init__(self, max_iter: int = 200) -> None:
        self.max_iter = max_iter

    def escape_time(self, c: complex) -> int:
        """Return iteration count before |z| > 2. max_iter if bounded."""
        z = 0.0 + 0.0j
        for n in range(self.max_iter):
            z = z * z + c
            if abs(z) > 2.0:
                return n
        return self.max_iter

    def render(
        self,
        re_min: float = -2.5,
        re_max: float = 1.0,
        im_min: float = -1.25,
        im_max: float = 1.25,
        width: int = 200,
        height: int = 100,
    ) -> np.ndarray:
        """Render escape time grid."""
        re_vals = np.linspace(re_min, re_max, width)
        im_vals = np.linspace(im_min, im_max, height)
        grid = np.zeros((height, width), dtype=int)
        for j, im in enumerate(im_vals):
            for i, re in enumerate(re_vals):
                grid[j, i] = self.escape_time(complex(re, im))
        return grid

    def eml_analysis(self) -> dict[str, object]:
        return {
            "name": "mandelbrot_set",
            "iteration_formula": "z -> z² + c  [EML-2 per step]",
            "eml_per_step": 2,
            "eml_boundary": "inf",
            "hausdorff_dim_boundary": 2,
            "proof": "Shishikura (1998): boundary has Hausdorff dim = 2",
            "insight": (
                "Mandelbrot: z_{n+1} = z_n² + c. "
                "In real coordinates: (x,y) -> (x²-y², 2xy) + (Re(c),Im(c)). "
                "Quadratic map → EML-2 per step. "
                "SET MEMBERSHIP is a limit (n→∞) → EML-inf to determine. "
                "Boundary is fractal (Hausdorff dim=2) → EML-inf geometry. "
                "The MAP is EML-2; the OBJECT (set) is EML-inf."
            ),
        }

    def boundary_complexity_test(self, n_sample: int = 1000) -> dict[str, object]:
        """Sample points on the boundary and measure local complexity."""
        rng = np.random.default_rng(42)
        # Sample from a thin ring near the boundary
        # by looking at points with escape times near max_iter
        re_vals = rng.uniform(-2.5, 1.0, n_sample)
        im_vals = rng.uniform(-1.25, 1.25, n_sample)
        escapes = np.array([
            self.escape_time(complex(r, i)) for r, i in zip(re_vals, im_vals)
        ])
        # Points near boundary: escape between 80-100% of max_iter
        near_boundary = (escapes > int(0.8 * self.max_iter)) & (escapes < self.max_iter)
        return {
            "n_sample": n_sample,
            "n_interior": int(np.sum(escapes == self.max_iter)),
            "n_exterior": int(np.sum(escapes < int(0.5 * self.max_iter))),
            "n_near_boundary": int(np.sum(near_boundary)),
            "boundary_fraction": float(np.sum(near_boundary)) / n_sample,
        }


# ── Julia Set ─────────────────────────────────────────────────────────────────

class JuliaSet:
    """
    Julia set J_c: same iteration z -> z² + c, but vary z_0, fix c.

    EML structure identical to Mandelbrot:
      - EML-2 per step
      - EML-inf set (fractal boundary for generic c)
      - Connected for c in Mandelbrot set, totally disconnected (Cantor) outside.
    """

    def __init__(self, c: complex = complex(-0.7269, 0.1889), max_iter: int = 200) -> None:
        self.c = c
        self.max_iter = max_iter

    def escape_time(self, z0: complex) -> int:
        z = z0
        for n in range(self.max_iter):
            z = z * z + self.c
            if abs(z) > 2.0:
                return n
        return self.max_iter

    def eml_analysis(self) -> dict[str, object]:
        return {
            "name": f"julia_set_c={self.c}",
            "iteration_formula": f"z -> z² + {self.c}  [EML-2 per step]",
            "eml_per_step": 2,
            "eml_boundary": "inf",
            "connected": "If c in Mandelbrot set; disconnected (Cantor) if c outside",
            "insight": (
                f"Julia set for c={self.c}: same z→z²+c iteration as Mandelbrot. "
                "EML-2 per step. The SET is EML-inf (fractal boundary). "
                "If c is in the Mandelbrot set, J_c is connected; else it's a Cantor dust "
                "(totally disconnected, EML-inf in the Cantor set sense)."
            ),
        }


# ── Fractal Taxonomy ──────────────────────────────────────────────────────────

FRACTAL_TAXONOMY: dict[str, dict[str, object]] = {
    "sierpinski_triangle": {
        "eml_per_step": 1,
        "eml_attractor": "inf",
        "hausdorff_dim": math.log(3) / math.log(2),
        "type": "IFS",
        "verdict": "EML-1 per affine step; fractal limit is EML-inf",
    },
    "koch_curve": {
        "eml_per_step": 2,
        "eml_attractor": "inf",
        "hausdorff_dim": math.log(4) / math.log(3),
        "type": "Subdivision",
        "verdict": "EML-2 per subdivision (rotation+scale); limit is EML-inf",
    },
    "mandelbrot_set": {
        "eml_per_step": 2,
        "eml_attractor": "inf",
        "hausdorff_dim": 2,
        "type": "Complex quadratic iteration",
        "verdict": "EML-2 per step z->z²+c; set boundary is EML-inf (Hausdorff dim=2)",
    },
    "julia_set": {
        "eml_per_step": 2,
        "eml_attractor": "inf",
        "hausdorff_dim": "1 (smooth) to 2 (fractal, c near boundary)",
        "type": "Complex quadratic iteration",
        "verdict": "EML-2 per step; connected/Cantor depending on c",
    },
    "cantor_set": {
        "eml_per_step": 1,
        "eml_attractor": "inf",
        "hausdorff_dim": math.log(2) / math.log(3),
        "type": "IFS (1D)",
        "verdict": "EML-1 per scale step (multiply by 1/3); Cantor limit is EML-inf",
    },
    "barnsley_fern": {
        "eml_per_step": 1,
        "eml_attractor": "inf",
        "hausdorff_dim": 1.9,
        "type": "IFS (4 affine maps)",
        "verdict": "EML-1 per affine step; fern shape is EML-inf limit",
    },
}


def analyze_fractal_eml() -> dict[str, object]:
    """Run complete fractal EML analysis."""
    # Koch curve subdivision
    koch = KochCurve()
    pts_1 = [complex(0), complex(1)]
    pts_5 = koch.iterate(pts_1, n_steps=5)
    n_segs_5 = len(pts_5) - 1

    # Mandelbrot boundary test
    mb = MandelbrotSet(max_iter=100)
    complexity = mb.boundary_complexity_test(n_sample=500)

    # Julia set analysis
    js = JuliaSet(c=complex(-0.7269, 0.1889))

    return {
        "koch": {
            "n_segments_after_5_steps": n_segs_5,
            "theory": 3 * (4**5),
            "hausdorff_dim": koch.hausdorff_dim,
            "eml_analysis": koch.eml_analysis(),
        },
        "mandelbrot": {
            "boundary_complexity": complexity,
            "eml_analysis": mb.eml_analysis(),
        },
        "julia": {
            "c": str(js.c),
            "eml_analysis": js.eml_analysis(),
        },
        "sierpinski": SierpinskiIFS().eml_analysis(),
        "taxonomy": FRACTAL_TAXONOMY,
        "key_insight": (
            "Universal fractal theorem (EML version): "
            "A fractal F generated by an EML-k iteration has EML-k per step "
            "but EML-inf geometry (the limit set). "
            "The gap between 'step complexity' and 'attractor complexity' is infinite. "
            "This is the fractal analogue of: pure tone (EML-3) vs noise (EML-inf). "
            "The iteration is analytic; infinite repetition produces non-analyticity."
        ),
    }


def fractal_taxonomy_table() -> str:
    lines = [
        f"  {'Fractal':24s}  {'EML/step':>9}  {'Attractor':>10}  {'Hausdorff dim':>14}  Type",
        "  " + "-"*24 + "  " + "-"*9 + "  " + "-"*10 + "  " + "-"*14 + "  " + "-"*20,
    ]
    for name, info in FRACTAL_TAXONOMY.items():
        hd = info["hausdorff_dim"]
        hd_str = f"{hd:.4f}" if isinstance(hd, float) else str(hd)
        lines.append(
            f"  {name:24s}  {str(info['eml_per_step']):>9}  {str(info['eml_attractor']):>10}"
            f"  {hd_str:>14s}  {info['type']}"
        )
    return "\n".join(lines)
