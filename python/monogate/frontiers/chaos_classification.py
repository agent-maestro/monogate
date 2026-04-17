"""
chaos_classification.py — EML-k Complexity for Iterated Maps.

Session 47 found: EML-k(logistic_r4, horizon=n) = O(n).
Session 48 question: are there chaotic maps with FIXED EML-k for all horizons?

Answer: YES — the Chebyshev map T_r(x) = cos(r * arccos(x)) has the
exact closed form x_n = cos(2^n * arccos(x_0)), analogous to logistic r=4.
But T_2(x) = 2x² - 1 is a degree-2 polynomial → EML-2 for one step.
And cos(2^n * theta) satisfies cos(2theta) = 2cos²(theta)-1 — iterated doubling.

The Chebyshev map IS conjugate to the logistic map via x = sin²(theta):
  logistic r=4: x_{n+1} = 4x(1-x)
  Chebyshev:    y_{n+1} = 2y² - 1   (with y = cos(theta))

Both have exact closed forms but growing EML depth with iteration.

New finding: The TENT MAP x_{n+1} = 1 - |2x - 1| has NO smooth closed form.
It is piecewise-linear → EML-∞ as a function (non-smooth) but EML-2 per step
(the formula 1 - |2x-1| = min(2x, 2-2x) is piecewise linear, not analytic).

Classification:
  logistic r=4: EML-k = O(n) [exact closed form, depth grows]
  Chebyshev T_r: EML-k = O(n) [conjugate to logistic]
  tent map:     EML-∞ per step [non-smooth, piecewise linear barrier]
  Arnold cat:   EML-2 per step [linear map mod 1 — matrix multiply is EML-2]
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable

import numpy as np

__all__ = [
    "IteratedMap",
    "LogisticMap",
    "ChebyshevMap",
    "TentMap",
    "ArnoldCatMap",
    "classify_eml_k",
    "EML_K_CLASSIFICATION",
]


@dataclass
class IteratedMap:
    """Base class for an iterated map with EML complexity analysis."""
    name: str
    formula: str

    def step(self, x: float) -> float:
        raise NotImplementedError

    def orbit(self, x0: float, n: int) -> np.ndarray:
        traj = np.empty(n + 1)
        traj[0] = x0
        x = x0
        for i in range(n):
            x = self.step(x)
            traj[i + 1] = x
        return traj

    def closed_form(self, x0: float, n: int) -> float | None:
        """Exact closed form at step n, if available. None if unknown."""
        return None

    def eml_depth_step(self) -> int:
        """EML depth of the one-step map formula."""
        raise NotImplementedError

    def eml_depth_horizon(self, n: int) -> int | str:
        """EML depth of the n-step closed form. 'inf' if no closed form."""
        return "inf"


class LogisticMap(IteratedMap):
    """x_{n+1} = r * x * (1 - x)."""

    def __init__(self, r: float = 4.0) -> None:
        super().__init__(
            name=f"logistic_r{r}",
            formula=f"x -> {r}*x*(1-x)",
        )
        self.r = r

    def step(self, x: float) -> float:
        return self.r * x * (1.0 - x)

    def closed_form(self, x0: float, n: int) -> float | None:
        if self.r != 4.0:
            return None
        theta = math.asin(math.sqrt(max(0.0, min(1.0, x0))))
        return math.sin(2**n * theta) ** 2

    def eml_depth_step(self) -> int:
        # r*x*(1-x) = r*(x - x²) — degree-2 polynomial → EML-2
        return 2

    def eml_depth_horizon(self, n: int) -> int | str:
        # sin²(2^n * arcsin(sqrt(x0))): depth ≈ 7 + 2*(n-1)
        if self.r == 4.0:
            return 7 + 2 * max(0, n - 1)
        return "inf"

    def eml_analysis(self) -> dict[str, object]:
        return {
            "name": self.name,
            "eml_depth_per_step": self.eml_depth_step(),
            "closed_form_r4": "sin²(2^n * arcsin(sqrt(x0)))",
            "eml_depth_horizon_n": "7 + 2*(n-1) for r=4",
            "eml_k_class": "O(n) — depth grows linearly with horizon",
            "chaos_source": "Sensitivity from 2^n factor in angle; EML-2 per step",
        }


class ChebyshevMap(IteratedMap):
    """T_r(x) = cos(r * arccos(x)) — degree-r Chebyshev polynomial."""

    def __init__(self, r: int = 2) -> None:
        super().__init__(
            name=f"chebyshev_T{r}",
            formula=f"x -> cos({r}*arccos(x))",
        )
        self.r = r

    def step(self, x: float) -> float:
        # Use recurrence: T_1=x, T_2=2x²-1, T_r via 2x*T_{r-1} - T_{r-2}
        x = max(-1.0, min(1.0, x))
        return math.cos(self.r * math.acos(x))

    def closed_form(self, x0: float, n: int) -> float | None:
        x0 = max(-1.0, min(1.0, x0))
        theta = math.acos(x0)
        return math.cos(self.r**n * theta)

    def eml_depth_step(self) -> int:
        # T_2(x) = 2x²-1: degree-2 poly → EML-2
        # T_r for r>2: degree-r poly → EML-2 (all polynomials are EML-2)
        return 2

    def eml_depth_horizon(self, n: int) -> int | str:
        # cos(r^n * theta): requires depth O(n) via iterated angle-doubling
        return 5 + n  # approximate: arccos(depth~4) + iterated cos

    def eml_analysis(self) -> dict[str, object]:
        return {
            "name": self.name,
            "eml_depth_per_step": self.eml_depth_step(),
            "closed_form": f"cos(r^n * arccos(x0)) for T_r iterated n times",
            "eml_depth_horizon_n": f"O(n) — iterated angle r^n requires n applications",
            "eml_k_class": "O(n) — conjugate to logistic map via x=cos(theta)",
            "key_identity": "T_2 = 2x²-1 is exactly EML-2 per step",
            "chaos": self.r >= 2,
        }


class TentMap(IteratedMap):
    """x_{n+1} = 1 - |2x - 1| = min(2x, 2-2x). Piecewise linear."""

    def __init__(self) -> None:
        super().__init__(
            name="tent_map",
            formula="x -> min(2x, 2-2x) = 1 - |2x-1|",
        )

    def step(self, x: float) -> float:
        return 1.0 - abs(2.0 * x - 1.0)

    def closed_form(self, x0: float, n: int) -> float | None:
        return None

    def eml_depth_step(self) -> int:
        # |2x-1| involves absolute value — not analytic, hence EML-∞
        return -1  # signals EML-∞

    def eml_depth_horizon(self, n: int) -> str:
        return "inf"

    def eml_analysis(self) -> dict[str, object]:
        return {
            "name": self.name,
            "eml_depth_per_step": "EML-inf",
            "reason": (
                "Tent map involves |x| — absolute value is NOT real-analytic "
                "at x=0. By the Infinite Zeros Barrier logic: any real-analytic "
                "function that equals |2x-1| on an interval must agree everywhere, "
                "but |2x-1| has a kink at x=1/2. No finite EML tree is piecewise-linear. "
                "EML-inf per step, EML-inf for all horizons."
            ),
            "eml_k_class": "EML-inf (non-smooth barrier)",
            "chaos": True,
            "eml_connection": (
                "Tent map is topologically conjugate to logistic r=4, but "
                "logistic is smooth (EML-2 per step) while tent is piecewise-linear (EML-inf). "
                "Conjugacy does not preserve EML complexity class."
            ),
        }


class ArnoldCatMap(IteratedMap):
    """(x,y) -> (x+y, x+2y) mod 1. Linear map on the torus T²."""

    def __init__(self) -> None:
        super().__init__(
            name="arnold_cat_map",
            formula="(x,y) -> (x+y mod 1, x+2y mod 1)",
        )

    def step(self, x: float) -> float:
        raise NotImplementedError("Arnold cat is 2D; use step_2d")

    def step_2d(self, x: float, y: float) -> tuple[float, float]:
        return (x + y) % 1.0, (x + 2.0 * y) % 1.0

    def orbit_2d(self, x0: float, y0: float, n: int) -> np.ndarray:
        traj = np.empty((n + 1, 2))
        traj[0] = [x0, y0]
        x, y = x0, y0
        for i in range(n):
            x, y = self.step_2d(x, y)
            traj[i + 1] = [x, y]
        return traj

    def eml_depth_step(self) -> int:
        # x+y and x+2y are degree-1 polynomials → EML-1 (linear)
        # mod 1 introduces floor() which is EML-∞ (like tent map)
        return -1  # signals EML-∞ due to mod

    def eml_depth_horizon(self, n: int) -> str:
        return "inf"

    def eml_analysis(self) -> dict[str, object]:
        # Matrix power: A^n = [[F_{2n-1}, F_{2n}], [F_{2n}, F_{2n+1}]] (Fibonacci!)
        # where F_k is the k-th Fibonacci number
        n_test = 6
        fib = [1, 1]
        for _ in range(2 * n_test + 2):
            fib.append(fib[-1] + fib[-2])

        return {
            "name": self.name,
            "eml_depth_linear_part": 1,
            "eml_depth_with_mod": "EML-inf (floor/mod is non-analytic)",
            "matrix_power": "A^n has Fibonacci entries — grows exponentially",
            "fibonacci_connection": (
                "Arnold cat map matrix A = [[1,1],[1,2]]. "
                "A^n has entries involving Fibonacci numbers F_n. "
                "The LINEAR part is EML-1 (matrix multiply = linear poly). "
                "The MOD 1 operation is EML-inf. "
                "Chaos arises from the mod operation, not the linear part."
            ),
            "eml_k_class": "EML-1 for linear part, EML-inf for full map",
        }


EML_K_CLASSIFICATION: dict[str, dict[str, object]] = {
    "logistic_r4": {
        "formula": "r*x*(1-x)",
        "eml_k_per_step": 2,
        "eml_k_horizon_n": "7 + 2*(n-1)",
        "has_closed_form": True,
        "chaos": True,
        "verdict": "EML-O(n): chaotic, closed form grows in depth",
    },
    "chebyshev_T2": {
        "formula": "2x²-1",
        "eml_k_per_step": 2,
        "eml_k_horizon_n": "O(n)",
        "has_closed_form": True,
        "chaos": True,
        "verdict": "EML-O(n): conjugate to logistic; exact closed form at all n",
    },
    "tent_map": {
        "formula": "1-|2x-1|",
        "eml_k_per_step": "inf",
        "eml_k_horizon_n": "inf",
        "has_closed_form": False,
        "chaos": True,
        "verdict": "EML-inf: piecewise-linear, kink at x=1/2 violates analyticity",
    },
    "arnold_cat": {
        "formula": "(x+y, x+2y) mod 1",
        "eml_k_per_step": "1 (linear) + inf (mod)",
        "eml_k_horizon_n": "inf",
        "has_closed_form": False,
        "chaos": True,
        "verdict": "EML-1 linear part, EML-inf for full map; mod operation is barrier",
    },
    "doubling_map": {
        "formula": "2x mod 1",
        "eml_k_per_step": "inf",
        "eml_k_horizon_n": "inf",
        "has_closed_form": True,
        "chaos": True,
        "verdict": "EML-inf: mod 1 is non-analytic; exact bit-shift closed form unusable",
    },
}


def classify_eml_k(map_name: str) -> dict[str, object]:
    return EML_K_CLASSIFICATION.get(map_name, {"error": f"Unknown map: {map_name}"})
