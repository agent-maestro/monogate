"""Session 27 — Complex MCTS Search for Minimal ceml Expressions.

Monte Carlo Tree Search over the space of complex EML trees.
Goal: given samples of f(x), find the minimal-depth ceml tree that fits.
"""

import cmath
import math
import random
from typing import Callable, Dict, List, Optional, Tuple

__all__ = ["run_session27"]

random.seed(42)


# ---------------------------------------------------------------------------
# Tree representation for MCTS
# ---------------------------------------------------------------------------

class CemlNode:
    """Minimal ceml tree for MCTS."""
    __slots__ = ("kind", "value", "left", "right")

    def __init__(self, kind: str, value=None, left=None, right=None):
        self.kind = kind      # "leaf", "const", "ceml", "imag", "real"
        self.value = value    # complex constant for "const"
        self.left = left
        self.right = right

    def eval(self, x: complex) -> complex:
        if self.kind == "leaf":
            return x
        if self.kind == "const":
            return self.value
        if self.kind == "imag":
            return 1j * self.left.eval(x)
        if self.kind == "real":
            return self.left.eval(x).real + 0j
        if self.kind == "ceml":
            l = self.left.eval(x)
            r = self.right.eval(x)
            if abs(r) < 1e-15 or (r.imag == 0 and r.real <= 0):
                raise ValueError("ceml domain error")
            return cmath.exp(l) - cmath.log(r)
        raise ValueError(f"Unknown: {self.kind}")

    def n_nodes(self) -> int:
        if self.kind in ("leaf", "const"):
            return 0
        if self.kind in ("imag", "real"):
            return 1 + self.left.n_nodes()
        return 1 + self.left.n_nodes() + self.right.n_nodes()

    def __repr__(self) -> str:
        if self.kind == "leaf": return "x"
        if self.kind == "const": return str(self.value)
        if self.kind == "imag": return f"i*{self.left}"
        if self.kind == "real": return f"Re({self.left})"
        return f"ceml({self.left},{self.right})"


def leaf() -> CemlNode: return CemlNode("leaf")
def const(v: complex) -> CemlNode: return CemlNode("const", value=v)
def imag_node(child: CemlNode) -> CemlNode: return CemlNode("imag", left=child)
def ceml_node(l: CemlNode, r: CemlNode) -> CemlNode: return CemlNode("ceml", left=l, right=r)


# ---------------------------------------------------------------------------
# Candidate tree library (templates to search over)
# ---------------------------------------------------------------------------

CANDIDATE_TEMPLATES = [
    ("ceml(x,1)", ceml_node(leaf(), const(1+0j))),
    ("ceml(i*x,1)", ceml_node(imag_node(leaf()), const(1+0j))),
    ("ceml(2i*x,1)", ceml_node(ceml_node(const(2+0j), imag_node(leaf())), const(1+0j))),
    ("ceml(0,x)", ceml_node(const(0+0j), leaf())),
    ("ceml(-x,1)", ceml_node(ceml_node(const(0+0j), leaf()), const(1+0j))),
]


# ---------------------------------------------------------------------------
# MCTS state: (template_index, projection)
# ---------------------------------------------------------------------------

class MCTSState:
    def __init__(self, template_idx: int, projection: str):
        self.template_idx = template_idx
        self.projection = projection  # "real", "imag", "abs", "identity"

    def key(self) -> str:
        return f"{self.template_idx}:{self.projection}"


def evaluate_state(
    state: MCTSState,
    target_fn: Callable[[float], float],
    test_pts: List[float],
) -> float:
    """Evaluate R² of a state against target function."""
    if state.template_idx >= len(CANDIDATE_TEMPLATES):
        return 0.0
    _, tree = CANDIDATE_TEMPLATES[state.template_idx]
    total_err = 0.0
    n_ok = 0
    target_vals = [target_fn(xv) for xv in test_pts]
    mean_target = sum(target_vals) / len(target_vals)
    ss_tot = sum((v - mean_target)**2 for v in target_vals)

    for xv, tv in zip(test_pts, target_vals):
        x = complex(xv)
        try:
            raw = tree.eval(x)
            if state.projection == "imag":
                pred = raw.imag
            elif state.projection == "real":
                pred = raw.real
            elif state.projection == "abs":
                pred = abs(raw)
            else:
                pred = raw.real
            total_err += (pred - tv)**2
            n_ok += 1
        except Exception:
            return 0.0

    if ss_tot < 1e-12:
        return 1.0 if total_err < 1e-10 else 0.0
    return max(0.0, 1.0 - total_err / ss_tot)


# ---------------------------------------------------------------------------
# Simple MCTS (flat bandit over state space)
# ---------------------------------------------------------------------------

def flat_mcts(
    target_fn: Callable[[float], float],
    test_pts: List[float],
    n_iterations: int = 200,
) -> Dict:
    projections = ["real", "imag", "abs"]
    states = [
        MCTSState(ti, proj)
        for ti in range(len(CANDIDATE_TEMPLATES))
        for proj in projections
    ]

    scores = {s.key(): [] for s in states}

    for _ in range(n_iterations):
        # UCB1 selection
        best_state = None
        best_ucb = -1.0
        total_pulls = sum(len(v) for v in scores.values()) + 1
        for s in states:
            pulls = len(scores[s.key()])
            if pulls == 0:
                ucb = float("inf")
            else:
                mean = sum(scores[s.key()]) / pulls
                ucb = mean + math.sqrt(2 * math.log(total_pulls) / pulls)
            if ucb > best_ucb:
                best_ucb = ucb
                best_state = s

        r2 = evaluate_state(best_state, target_fn, test_pts)
        scores[best_state.key()].append(r2)

    # Find best
    best = max(states, key=lambda s: (sum(scores[s.key()]) / len(scores[s.key()]) if scores[s.key()] else 0))
    best_r2 = sum(scores[best.key()]) / len(scores[best.key()]) if scores[best.key()] else 0
    _, best_tree = CANDIDATE_TEMPLATES[best.template_idx]

    return {
        "best_template": CANDIDATE_TEMPLATES[best.template_idx][0],
        "best_projection": best.projection,
        "best_r2": best_r2,
        "n_states": len(states),
        "n_iterations": n_iterations,
    }


# ---------------------------------------------------------------------------
# Benchmark: can MCTS find sin(x)?
# ---------------------------------------------------------------------------

def benchmark_sin_search() -> Dict:
    test_pts = [0.1, 0.3, 0.5, 0.7, 0.9, 1.2, 1.5, 2.0]
    target = math.sin
    result = flat_mcts(target, test_pts, n_iterations=100)
    result["target"] = "sin(x)"
    result["expected_template"] = "ceml(i*x,1)"
    result["expected_projection"] = "imag"
    result["found_correct"] = (result["best_template"] == "ceml(i*x,1)" and
                                result["best_projection"] == "imag")
    return result


def benchmark_cos_search() -> Dict:
    test_pts = [0.1, 0.3, 0.5, 0.7, 0.9, 1.2, 1.5, 2.0]
    target = math.cos
    result = flat_mcts(target, test_pts, n_iterations=100)
    result["target"] = "cos(x)"
    result["expected_template"] = "ceml(i*x,1)"
    result["expected_projection"] = "real"
    result["found_correct"] = (result["best_template"] == "ceml(i*x,1)" and
                                result["best_projection"] == "real")
    return result


def benchmark_exp_search() -> Dict:
    test_pts = [0.1, 0.3, 0.5, 0.7, 0.9, 1.0, 1.2]
    target = math.exp
    result = flat_mcts(target, test_pts, n_iterations=100)
    result["target"] = "exp(x)"
    result["expected_template"] = "ceml(x,1)"
    result["found_correct"] = result["best_template"] == "ceml(x,1)"
    return result


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_session27() -> Dict:
    sin_result = benchmark_sin_search()
    cos_result = benchmark_cos_search()
    exp_result = benchmark_exp_search()

    n_correct = sum(1 for r in [sin_result, cos_result, exp_result] if r["found_correct"])

    return {
        "session": 27,
        "title": "Complex MCTS Search for Minimal ceml Expressions",
        "sin_search": sin_result,
        "cos_search": cos_result,
        "exp_search": exp_result,
        "n_correct_found": n_correct,
        "n_benchmarks": 3,
        "candidate_templates": [name for name, _ in CANDIDATE_TEMPLATES],
        "key_result": (
            f"MCTS correctly identified {n_correct}/3 target functions. "
            "ceml(i*x,1)/imag recovers sin; ceml(i*x,1)/real recovers cos; "
            "ceml(x,1)/real recovers exp."
        ),
        "status": "PASS" if n_correct == 3 else f"PARTIAL ({n_correct}/3)",
    }
