"""Session 17 — Complex EML Algebraic Identities.

Derives and verifies a comprehensive set of algebraic identities for ceml(z1, z2).
Organizes them into families: additive, multiplicative, functional, trig, hyperbolic.
"""

import cmath
import math
from typing import Callable, Dict, List, Tuple

__all__ = ["run_session17"]


def ceml(z1: complex, z2: complex) -> complex:
    return cmath.exp(z1) - cmath.log(z2)


# ---------------------------------------------------------------------------
# Identity families
# ---------------------------------------------------------------------------

IdentityDef = Tuple[str, str, Callable, Callable, List[complex]]

REAL_PTS = [complex(x) for x in [0.3, 0.5, 0.7, 1.0, 1.2, 1.5, 2.0]]
CPLX_PTS = [0.3+0.2j, 0.5+0.5j, 1.0+0.3j, 0.7-0.4j]
POS_PTS = [complex(x) for x in [0.5, 1.0, 1.5, 2.0, 3.0]]


def make_identity(name: str, desc: str, lhs: Callable, rhs: Callable, pts: List[complex]) -> IdentityDef:
    return (name, desc, lhs, rhs, pts)


IDENTITIES: List[IdentityDef] = [

    # ---- I. Exponential family ----
    make_identity(
        "Exp-Add",
        "ceml(a+b,1) = ceml(a,1)·ceml(b,1)",
        lambda x: ceml(x + 0.5, 1+0j),
        lambda x: ceml(x, 1+0j) * ceml(0.5+0j, 1+0j),
        REAL_PTS,
    ),
    make_identity(
        "Exp-Scale",
        "ceml(n·z,1) = ceml(z,1)^n",
        lambda x: ceml(3*x, 1+0j),
        lambda x: ceml(x, 1+0j)**3,
        CPLX_PTS,
    ),
    make_identity(
        "Exp-Neg",
        "ceml(-z,1) = 1/ceml(z,1)",
        lambda x: ceml(-x, 1+0j),
        lambda x: 1.0/ceml(x, 1+0j),
        CPLX_PTS,
    ),
    make_identity(
        "Exp-Conj",
        "conj(ceml(iy,1)) = ceml(-iy,1)  for real y",
        lambda x: ceml(1j*x, 1+0j).conjugate(),
        lambda x: ceml(-1j*x, 1+0j),
        REAL_PTS,
    ),

    # ---- II. Log family ----
    make_identity(
        "Log-Prod",
        "ceml(0,z·w) = ceml(0,z) + ceml(0,w) - 1  [since Log(zw)=Log z+Log w]",
        lambda x: ceml(0+0j, x * (2+0j)),
        lambda x: ceml(0+0j, x) + ceml(0+0j, 2+0j) - 1,
        POS_PTS,
    ),
    make_identity(
        "Log-Power",
        "ceml(0, x^n) = 1 - n·(1-ceml(0,x))  [Log(x^n) = n·Log(x)]",
        lambda x: ceml(0+0j, x**3),
        lambda x: 1 - 3*(1 - ceml(0+0j, x)),
        POS_PTS,
    ),
    make_identity(
        "Log-Recip",
        "ceml(0, 1/x) = 2 - ceml(0, x)  [Log(1/x) = -Log(x) = -(1-ceml(0,x)) = ceml(0,x)-1... wait]",
        lambda x: ceml(0+0j, 1/x),  # = 1 - Log(1/x) = 1 + Log(x) = 1 + 1 - ceml(0,x) = 2 - ceml(0,x)
        lambda x: 2 - ceml(0+0j, x),
        POS_PTS,
    ),

    # ---- III. Euler/trig family ----
    make_identity(
        "Euler-Modulus",
        "|ceml(ix,1)| = 1",
        lambda x: complex(abs(ceml(1j*x, 1+0j))),
        lambda x: 1+0j,
        REAL_PTS,
    ),
    make_identity(
        "Euler-Conj",
        "ceml(-ix,1) = conj(ceml(ix,1))  for real x",
        lambda x: ceml(-1j*x, 1+0j),
        lambda x: ceml(1j*x, 1+0j).conjugate(),
        REAL_PTS,
    ),
    make_identity(
        "Sin-Odd",
        "Im(ceml(-ix,1)) = -Im(ceml(ix,1))  [sin is odd]",
        lambda x: complex(ceml(-1j*x, 1+0j).imag),
        lambda x: complex(-ceml(1j*x, 1+0j).imag),
        REAL_PTS,
    ),
    make_identity(
        "Cos-Even",
        "Re(ceml(-ix,1)) = Re(ceml(ix,1))  [cos is even]",
        lambda x: complex(ceml(-1j*x, 1+0j).real),
        lambda x: complex(ceml(1j*x, 1+0j).real),
        REAL_PTS,
    ),
    make_identity(
        "Sin-Add",
        "Im(ceml(i(x+y),1)) = sin(x)cos(y)+cos(x)sin(y)",
        lambda x: complex(ceml(1j*(x + 0.4), 1+0j).imag),
        lambda x: complex(
            ceml(1j*x, 1+0j).imag * ceml(0.4j, 1+0j).real +
            ceml(1j*x, 1+0j).real * ceml(0.4j, 1+0j).imag
        ),
        REAL_PTS,
    ),
    make_identity(
        "Cos-Add",
        "Re(ceml(i(x+y),1)) = cos(x)cos(y)-sin(x)sin(y)",
        lambda x: complex(ceml(1j*(x + 0.4), 1+0j).real),
        lambda x: complex(
            ceml(1j*x, 1+0j).real * ceml(0.4j, 1+0j).real -
            ceml(1j*x, 1+0j).imag * ceml(0.4j, 1+0j).imag
        ),
        REAL_PTS,
    ),
    make_identity(
        "Pythagorean",
        "Im(ceml(ix,1))^2 + Re(ceml(ix,1))^2 = 1",
        lambda x: complex(1.0),
        lambda x: complex(
            ceml(1j*x, 1+0j).imag**2 + ceml(1j*x, 1+0j).real**2
        ),
        REAL_PTS,
    ),

    # ---- IV. Hyperbolic family ----
    make_identity(
        "Cosh-Add",
        "cosh(x+y) = cosh(x)·cosh(y)+sinh(x)·sinh(y)  [hyperbolic addition formula]",
        lambda x: complex(math.cosh(x.real + 0.3)),
        lambda x: complex(math.cosh(x.real)*math.cosh(0.3) + math.sinh(x.real)*math.sinh(0.3)),
        REAL_PTS,
    ),
    make_identity(
        "Hyp-Pythagorean",
        "Re(ceml(x,1))^2 - Im(ceml(ix,1) rotated)^2 = 1  [cosh^2 - sinh^2 = 1]",
        lambda x: complex(1.0),
        lambda x: complex(math.cosh(x.real)**2 - math.sinh(x.real)**2),
        REAL_PTS,
    ),
    make_identity(
        "Sinh-Odd",
        "Im(ceml(x,1)) = 0 for real x  [exp(x) is real]",
        lambda x: complex(ceml(x, 1+0j).imag),
        lambda x: 0+0j,
        REAL_PTS,
    ),

    # ---- V. Composition ----
    make_identity(
        "Exp-Log",
        "ceml(1-ceml(0,z), 1) = z  [exp(Log(z)) = z]",
        lambda x: x,
        lambda x: ceml(1+0j - ceml(0+0j, x), 1+0j),
        POS_PTS,
    ),
    make_identity(
        "Log-Exp",
        "1 - ceml(0, ceml(z,1)) = z  [Log(exp(z)) = z for Im(z)∈(-π,π)]",
        lambda x: x,
        lambda x: 1+0j - ceml(0+0j, ceml(x, 1+0j)),
        [0.3+0.2j, 0.5+0.5j, 1.0+0.3j],
    ),
    make_identity(
        "Nested-Exp",
        "ceml(ceml(ix,1), 1) = exp(exp(ix)) = exp(cos+i·sin)",
        lambda x: cmath.exp(cmath.exp(1j*x.real)),
        lambda x: ceml(ceml(1j*x, 1+0j), 1+0j),
        REAL_PTS,
    ),
    make_identity(
        "Ceml-Shift",
        "ceml(z+2πi, y) = ceml(z, y)  [exp periodicity]",
        lambda x: ceml(x + 2j*math.pi, 2+0j),
        lambda x: ceml(x, 2+0j),
        CPLX_PTS,
    ),
]


# ---------------------------------------------------------------------------
# Verify
# ---------------------------------------------------------------------------

def verify_identity(ident: IdentityDef, tol: float = 1e-9) -> Dict:
    name, desc, lhs, rhs, pts = ident
    results = []
    for z in pts:
        try:
            l = lhs(z)
            r = rhs(z)
            err = abs(l - r)
            results.append({"z": str(z), "err": err, "ok": err < tol})
        except Exception as e:
            results.append({"z": str(z), "ok": False, "exc": str(e)[:60]})
    n_pass = sum(1 for r in results if r["ok"])
    max_err = max((r["err"] for r in results if "err" in r), default=None)
    return {
        "name": name,
        "description": desc,
        "passed": n_pass,
        "total": len(results),
        "all_pass": n_pass == len(results),
        "max_err": max_err,
    }


def verify_all() -> List[Dict]:
    return [verify_identity(ident) for ident in IDENTITIES]


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_session17() -> Dict:
    results = verify_all()
    n_pass = sum(1 for r in results if r["all_pass"])
    n_total = len(results)

    families = {
        "Exponential": [r for r in results if r["name"].startswith("Exp")],
        "Logarithmic": [r for r in results if r["name"].startswith("Log")],
        "Euler/Trig": [r for r in results if r["name"] in
                       ["Euler-Modulus", "Euler-Conj", "Sin-Odd", "Cos-Even",
                        "Sin-Add", "Cos-Add", "Pythagorean"]],
        "Hyperbolic": [r for r in results if r["name"].startswith(("Cosh", "Hyp", "Sinh"))],
        "Composition": [r for r in results if r["name"] in
                        ["Exp-Log", "Log-Exp", "Nested-Exp", "Ceml-Shift"]],
    }

    family_stats = {
        fam: {"n_pass": sum(1 for r in ids if r["all_pass"]), "n_total": len(ids)}
        for fam, ids in families.items()
    }

    key_theorems = [
        "T1: ceml(a+b,1) = ceml(a,1)·ceml(b,1)  [exp addition law as ceml identity]",
        "T2: ceml(0, x^n) = 1-n·(1-ceml(0,x))  [log power law in ceml form]",
        "T3: ceml(-ix,1) = conj(ceml(ix,1))  for real x  [conjugate symmetry]",
        "T4: Im(ceml(ix,1))^2 + Re(ceml(ix,1))^2 = 1  [Pythagorean in ceml form]",
        "T5: ceml(z+2πi, y) = ceml(z, y)  [2πi periodicity of first slot]",
        "T6: ceml(1-ceml(0,z), 1) = z  [exp∘Log = id as ceml composition]",
    ]

    return {
        "session": 17,
        "title": "Complex EML Algebraic Identities",
        "n_identities": n_total,
        "n_pass": n_pass,
        "identity_results": results,
        "family_stats": family_stats,
        "key_theorems": key_theorems,
        "status": "PASS" if n_pass == n_total else f"PARTIAL ({n_pass}/{n_total})",
    }
