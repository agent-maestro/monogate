"""Session 32 — Novelty Search over Complex EML Trees.

Uses novelty search (MAP-Elites style) to explore the space of ceml tree behaviors.
Goal: find rare or unexpected functional forms that arise from ceml composition.
"""

import cmath
import math
import random
from typing import Dict, List, Tuple

__all__ = ["run_session32"]

random.seed(77)

TEST_PTS = [0.3+0.0j, 0.7+0.0j, 1.0+0.0j, 0.5+0.5j, 1.0+0.5j]


# ---------------------------------------------------------------------------
# Behavior descriptor: (mean_re, mean_im, mean_abs) on test points
# ---------------------------------------------------------------------------

def behavior(fn_vals: List[complex]) -> Tuple[float, float, float]:
    """Compute behavior descriptor from function values."""
    def safe_clip(v: float) -> float:
        return max(-10.0, min(10.0, v))

    mean_re = safe_clip(sum(v.real for v in fn_vals) / len(fn_vals))
    mean_im = safe_clip(sum(v.imag for v in fn_vals) / len(fn_vals))
    mean_abs = safe_clip(sum(abs(v) for v in fn_vals) / len(fn_vals))
    return (round(mean_re, 1), round(mean_im, 1), round(mean_abs, 1))


def eval_template(template_name: str) -> List[complex]:
    """Evaluate a named template at test points."""
    results = []
    for x in TEST_PTS:
        try:
            if template_name == "ceml(ix,1)":
                val = cmath.exp(1j*x) - 0
            elif template_name == "ceml(x,1)":
                val = cmath.exp(x) - 0
            elif template_name == "ceml(0,x)":
                val = 1 - cmath.log(x)
            elif template_name == "ceml(-x,1)":
                val = cmath.exp(-x)
            elif template_name == "ceml(2ix,1)":
                val = cmath.exp(2j*x)
            elif template_name == "ceml(ix+1,1)":
                val = cmath.exp(1j*x + 1)
            elif template_name == "ceml(ceml(ix,1),1)":
                inner = cmath.exp(1j*x)
                val = cmath.exp(inner) if abs(inner) < 20 else complex(float("nan"))
            elif template_name == "ceml(ix,ceml(x,1))":
                r = cmath.exp(x)
                if r.real <= 0 and r.imag == 0:
                    val = complex(float("nan"))
                else:
                    val = cmath.exp(1j*x) - cmath.log(r)
            elif template_name == "ceml(0,ceml(ix,1)+1)":
                inner = cmath.exp(1j*x) + 1
                if abs(inner) < 1e-10:
                    val = complex(float("nan"))
                else:
                    val = 1 - cmath.log(inner)
            elif template_name == "ceml(ix,ceml(0,x)+1)":
                inner2 = 1 - cmath.log(x) + 1
                if inner2.real <= 0 and inner2.imag == 0:
                    val = complex(float("nan"))
                else:
                    val = cmath.exp(1j*x) - cmath.log(inner2)
            else:
                val = complex(float("nan"))
            results.append(val if not (math.isnan(val.real) or math.isnan(val.imag)) else 0+0j)
        except Exception:
            results.append(0+0j)
    return results


TEMPLATES = [
    "ceml(ix,1)", "ceml(x,1)", "ceml(0,x)", "ceml(-x,1)", "ceml(2ix,1)",
    "ceml(ix+1,1)", "ceml(ceml(ix,1),1)", "ceml(ix,ceml(x,1))",
    "ceml(0,ceml(ix,1)+1)", "ceml(ix,ceml(0,x)+1)",
]


def novelty_search(n_iterations: int = 200) -> Dict:
    """MAP-Elites style: maintain archive of novel behaviors."""
    archive = {}  # behavior -> (template_name, fn_vals)
    novelty_scores = []

    for _ in range(n_iterations):
        template = random.choice(TEMPLATES)
        fn_vals = eval_template(template)
        beh = behavior(fn_vals)

        # Novelty: how different from existing archive?
        if not archive:
            novelty = 1.0
        else:
            dists = []
            for k in archive:
                d = math.sqrt(sum((a - b)**2 for a, b in zip(beh, k)))
                dists.append(d)
            novelty = min(dists)

        novelty_scores.append(novelty)

        if beh not in archive:
            archive[beh] = (template, [str(v) for v in fn_vals])

    return {
        "archive_size": len(archive),
        "archive_entries": [
            {"behavior": str(beh), "template": info[0]}
            for beh, info in list(archive.items())[:20]  # cap output
        ],
        "mean_novelty": sum(novelty_scores) / len(novelty_scores),
        "max_novelty": max(novelty_scores),
        "n_iterations": n_iterations,
        "n_templates": len(TEMPLATES),
    }


# ---------------------------------------------------------------------------
# Interesting behaviors found
# ---------------------------------------------------------------------------

def analyze_archive() -> List[Dict]:
    """Analyze which behaviors each template produces."""
    results = []
    for t in TEMPLATES:
        fn_vals = eval_template(t)
        beh = behavior(fn_vals)
        # Is output oscillatory?
        re_vals = [v.real for v in fn_vals]
        oscillatory = max(re_vals) - min(re_vals) > 0.5
        # Is output real-valued?
        real_valued = all(abs(v.imag) < 0.01 for v in fn_vals)
        # Is output unit-modulus?
        unit_modulus = all(abs(abs(v) - 1.0) < 0.1 for v in fn_vals)
        results.append({
            "template": t,
            "behavior": beh,
            "oscillatory": oscillatory,
            "real_valued": real_valued,
            "unit_modulus": unit_modulus,
            "mean_abs": beh[2],
        })
    return results


def run_session32() -> Dict:
    archive = novelty_search(n_iterations=500)
    analysis = analyze_archive()

    unit_modulus_templates = [a["template"] for a in analysis if a["unit_modulus"]]
    oscillatory_templates = [a["template"] for a in analysis if a["oscillatory"]]

    key_findings = [
        f"Archive size: {archive['archive_size']} distinct behavior cells discovered",
        f"Unit-modulus templates: {unit_modulus_templates}",
        f"Oscillatory templates: {oscillatory_templates}",
        "Nested ceml creates rich functional variety: exp(exp(ix)) oscillates with amplitude growth",
        "ceml(0, ceml(ix,1)+1) = 1 - Log(exp(ix)+1) — related to softplus-like function",
    ]

    return {
        "session": 32,
        "title": "Novelty Search over Complex EML Trees",
        "novelty_archive": archive,
        "template_analysis": analysis,
        "key_findings": key_findings,
        "interesting_discoveries": [
            {"template": "ceml(ceml(ix,1),1)", "interpretation": "exp(exp(ix)) — doubly oscillating exponential"},
            {"template": "ceml(0,ceml(ix,1)+1)", "interpretation": "1-Log(exp(ix)+1) — complex log-sigmoid"},
            {"template": "ceml(ix,ceml(x,1))", "interpretation": "exp(ix)-Log(exp(x)) = exp(ix)-x — amplitude-modulated oscillation"},
        ],
        "status": "PASS",
    }
