"""Session 19 — Complex EML Depth Collapse Census.

Systematic scan of DLMF/standard mathematical functions.
Classifies each by complex EML depth: 1, 2, 3, or ∞.

Classification criteria:
  EML-1: f(x) = proj(ceml(g(x), 1)) for some g, where proj = Re/Im/abs
  EML-2: f requires composition of exactly 2 ceml nodes
  EML-3: f requires 3 ceml nodes
  EML-∞: no finite ceml tree computes f exactly
"""

import cmath
import math
from typing import Dict, List, Optional

__all__ = ["run_session19"]


# ---------------------------------------------------------------------------
# DLMF function census
# ---------------------------------------------------------------------------

CENSUS: List[Dict] = [

    # ========= EML-1 over ℂ =========
    {
        "function": "exp(x)",
        "category": "Elementary",
        "complex_eml_depth": 1,
        "formula": "ceml(x, 1)",
        "justification": "Direct definition: ceml(z,1) = exp(z)",
        "euler_gateway": False,
    },
    {
        "function": "sin(x)",
        "category": "Trigonometric",
        "complex_eml_depth": 1,
        "formula": "Im(ceml(ix, 1))",
        "justification": "Euler: Im(exp(ix)) = sin(x)",
        "euler_gateway": True,
    },
    {
        "function": "cos(x)",
        "category": "Trigonometric",
        "complex_eml_depth": 1,
        "formula": "Re(ceml(ix, 1))",
        "justification": "Euler: Re(exp(ix)) = cos(x)",
        "euler_gateway": True,
    },
    {
        "function": "tan(x)",
        "category": "Trigonometric",
        "complex_eml_depth": 1,
        "formula": "Im(ceml(ix,1)) / Re(ceml(ix,1))",
        "justification": "tan = sin/cos, both from same depth-1 ceml",
        "euler_gateway": True,
    },
    {
        "function": "csc(x)",
        "category": "Trigonometric",
        "complex_eml_depth": 1,
        "formula": "1 / Im(ceml(ix,1))",
        "justification": "csc = 1/sin",
        "euler_gateway": True,
    },
    {
        "function": "sec(x)",
        "category": "Trigonometric",
        "complex_eml_depth": 1,
        "formula": "1 / Re(ceml(ix,1))",
        "justification": "sec = 1/cos",
        "euler_gateway": True,
    },
    {
        "function": "cot(x)",
        "category": "Trigonometric",
        "complex_eml_depth": 1,
        "formula": "Re(ceml(ix,1)) / Im(ceml(ix,1))",
        "justification": "cot = cos/sin",
        "euler_gateway": True,
    },
    {
        "function": "sinh(x)",
        "category": "Hyperbolic",
        "complex_eml_depth": 1,
        "formula": "Im(ceml(i(-ix),1)) = (ceml(x,1)-ceml(-x,1))/2",
        "justification": "sinh(x) = -i*sin(ix) = Im(ceml(-i*(ix),1))",
        "euler_gateway": True,
    },
    {
        "function": "cosh(x)",
        "category": "Hyperbolic",
        "complex_eml_depth": 1,
        "formula": "Re(ceml(i(-ix),1)) = (ceml(x,1)+ceml(-x,1))/2",
        "justification": "cosh(x) = cos(ix) = Re(exp(i*(ix)))",
        "euler_gateway": True,
    },
    {
        "function": "tanh(x)",
        "category": "Hyperbolic",
        "complex_eml_depth": 1,
        "formula": "Im(ceml(-ix,1)) / Re(ceml(-ix,1)) [via sinh/cosh]",
        "justification": "tanh = sinh/cosh",
        "euler_gateway": True,
    },
    {
        "function": "exp(i*omega*x) [Fourier mode]",
        "category": "Fourier",
        "complex_eml_depth": 1,
        "formula": "ceml(i*omega*x, 1)",
        "justification": "Direct: ceml(i*omega*x, 1) = exp(i*omega*x)",
        "euler_gateway": True,
    },
    {
        "function": "e^x * cos(x)",
        "category": "Damped Oscillation",
        "complex_eml_depth": 1,
        "formula": "Re(ceml((1+i)x, 1))",
        "justification": "Re(exp((1+i)x)) = e^x*cos(x)",
        "euler_gateway": True,
    },
    {
        "function": "e^x * sin(x)",
        "category": "Damped Oscillation",
        "complex_eml_depth": 1,
        "formula": "Im(ceml((1+i)x, 1))",
        "justification": "Im(exp((1+i)x)) = e^x*sin(x)",
        "euler_gateway": True,
    },
    {
        "function": "cos(omega*x + phi)",
        "category": "Phase-shifted Trig",
        "complex_eml_depth": 1,
        "formula": "Re(ceml(i*(omega*x+phi), 1))",
        "justification": "Phase shift absorbed into argument of ceml",
        "euler_gateway": True,
    },
    {
        "function": "Chebyshev T_n(cos(theta)) = cos(n*theta)",
        "category": "Orthogonal Polynomials",
        "complex_eml_depth": 1,
        "formula": "Re(ceml(i*n*theta, 1))",
        "justification": "On unit circle, T_n(cos θ) = cos(nθ) = Re(ceml(inθ,1))",
        "euler_gateway": True,
    },

    # ========= EML-2 over ℂ =========
    {
        "function": "x^n (integer power, x>0)",
        "category": "Power",
        "complex_eml_depth": 2,
        "formula": "ceml(n*(1-ceml(0,x)), 1)",
        "justification": "x^n = exp(n*Log(x)); Log(x)=1-ceml(0,x) [arithmetic]; depth 2",
        "euler_gateway": False,
    },
    {
        "function": "x^alpha (real power, x>0)",
        "category": "Power",
        "complex_eml_depth": 2,
        "formula": "ceml(alpha*(1-ceml(0,x)), 1)",
        "justification": "Same as x^n",
        "euler_gateway": False,
    },
    {
        "function": "arctan(x)",
        "category": "Inverse Trig",
        "complex_eml_depth": 2,
        "formula": "(i/2)*(1-ceml(0,(1+ix)/(1-ix)))",
        "justification": "arctan(x) = (i/2)*Log((1-ix)/(1+ix)); Log = 1-ceml(0,·)",
        "euler_gateway": False,
    },
    {
        "function": "arcsinh(x)",
        "category": "Inverse Hyperbolic",
        "complex_eml_depth": 2,
        "formula": "1-ceml(0, x+sqrt(x^2+1))",
        "justification": "arcsinh(x) = Log(x+sqrt(x^2+1))",
        "euler_gateway": False,
    },
    {
        "function": "arctanh(x)",
        "category": "Inverse Hyperbolic",
        "complex_eml_depth": 2,
        "formula": "(1-ceml(0,(1+x)/(1-x)))/2",
        "justification": "arctanh(x) = (1/2)*Log((1+x)/(1-x))",
        "euler_gateway": False,
    },
    {
        "function": "log(sin(x))",
        "category": "Composite",
        "complex_eml_depth": 2,
        "formula": "1-ceml(0, Im(ceml(ix,1)))",
        "justification": "Log(sin(x)); sin = Im(depth-1); Log = 1-ceml(0,·)",
        "euler_gateway": True,
    },
    {
        "function": "exp(sin(x))",
        "category": "Composite",
        "complex_eml_depth": 2,
        "formula": "ceml(Im(ceml(ix,1)), 1)",
        "justification": "exp∘sin: inner ceml gives sin, outer exp via second ceml",
        "euler_gateway": True,
    },
    {
        "function": "sin(exp(x))",
        "category": "Composite",
        "complex_eml_depth": 2,
        "formula": "Im(ceml(i*ceml(x,1), 1))",
        "justification": "sin(exp(x)) = Im(exp(i*exp(x))); exp(x)=ceml(x,1)",
        "euler_gateway": True,
    },

    # ========= EML-3 over ℂ =========
    {
        "function": "arcsin(x)",
        "category": "Inverse Trig",
        "complex_eml_depth": 3,
        "formula": "-i*Log(ix + sqrt(1-x^2)); needs 3 ceml for Log and sqrt",
        "justification": "arcsin = -i*(1-ceml(0, ix+sqrt(1-x^2))); sqrt needs depth 2",
        "euler_gateway": False,
    },
    {
        "function": "arccos(x)",
        "category": "Inverse Trig",
        "complex_eml_depth": 3,
        "formula": "pi/2 - arcsin(x); inherits arcsin depth",
        "justification": "arccos = π/2 - arcsin; same depth",
        "euler_gateway": False,
    },
    {
        "function": "Log(x) [pure tree form]",
        "category": "Logarithm",
        "complex_eml_depth": 3,
        "formula": "ceml(1, ceml(ceml(1,x), 1))  [from ln_eml in core]",
        "justification": "ln_eml = ceml(1, ceml(ceml(1,x),1)); depth 3 (same as real)",
        "euler_gateway": False,
    },
    {
        "function": "sin(log(x))",
        "category": "Composite",
        "complex_eml_depth": 3,
        "formula": "Im(ceml(i*(1-ceml(0,x)), 1)); 2 ceml + arithmetic or 3 pure",
        "justification": "sin(Log(x)); Log depth 3 over pure trees",
        "euler_gateway": True,
    },

    # ========= EML-∞ (conjectured) =========
    {
        "function": "Riemann zeta ζ(s)",
        "category": "Number Theory",
        "complex_eml_depth": "∞",
        "formula": "∑ n^(-s) — infinite sum, no finite ceml tree",
        "justification": "No finite composition of exp and Log gives the Dirichlet series",
        "euler_gateway": False,
    },
    {
        "function": "Gamma Γ(z) (exact)",
        "category": "Special",
        "complex_eml_depth": "∞",
        "formula": "Stirling approx is EML-2; exact Γ requires infinite product",
        "justification": "Γ(z) = ∫ t^{z-1}e^{-t}dt — integral representation, not EML-finite",
        "euler_gateway": False,
    },
    {
        "function": "Bessel J_n(x) (exact)",
        "category": "Special",
        "complex_eml_depth": "∞",
        "formula": "J_n = sum of infinitely many trig integrals",
        "justification": "No finite ceml tree; Fourier series has ∞ terms",
        "euler_gateway": False,
    },
    {
        "function": "Weierstrass P(z)",
        "category": "Elliptic",
        "complex_eml_depth": "∞",
        "formula": "Double-periodic, not expressible as finite ceml composition",
        "justification": "Elliptic functions transcend the single-period structure of exp",
        "euler_gateway": False,
    },
    {
        "function": "Modular j-function",
        "category": "Modular",
        "complex_eml_depth": "∞",
        "formula": "j(τ) = q^{-1} + 744 + ...; infinite q-expansion",
        "justification": "Modular symmetry under SL2(Z) precludes finite ceml form",
        "euler_gateway": False,
    },
]


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------

def census_statistics(census: List[Dict]) -> Dict:
    by_depth = {}
    for entry in census:
        d = str(entry["complex_eml_depth"])
        by_depth.setdefault(d, [])
        by_depth[d].append(entry["function"])

    euler_count = sum(1 for e in census if e.get("euler_gateway", False))

    return {
        "total_functions": len(census),
        "by_depth": {k: {"count": len(v), "functions": v} for k, v in by_depth.items()},
        "euler_gateway_count": euler_count,
        "fraction_collapsible": f"{sum(1 for e in census if e['complex_eml_depth'] != '∞')}/{len(census)}",
    }


# ---------------------------------------------------------------------------
# Numerical spot-checks
# ---------------------------------------------------------------------------

def spot_checks() -> List[Dict]:
    results = []
    x = 0.8

    checks = [
        ("sin(x)", cmath.exp(1j*x).imag, math.sin(x)),
        ("cos(x)", cmath.exp(1j*x).real, math.cos(x)),
        ("e^x*cos(x)", cmath.exp((1+1j)*x).real, math.exp(x)*math.cos(x)),
        ("e^x*sin(x)", cmath.exp((1+1j)*x).imag, math.exp(x)*math.sin(x)),
        # x^3 = exp(3*Log(x)); Log(x) = cmath.log(x); ceml(0,x)=1-log(x) so 1-ceml(0,x)=log(x)
        ("x^3 via depth-2", cmath.exp(3 * cmath.log(complex(x))).real, x**3),
        ("sin(exp(x))", cmath.exp(1j*cmath.exp(complex(x))).imag, math.sin(math.exp(x))),
        ("exp(sin(x))", cmath.exp(complex(math.sin(x))).real, math.exp(math.sin(x))),
    ]

    for name, val, ref in checks:
        err = abs(val - ref)
        results.append({"fn": name, "val": float(val) if isinstance(val, complex) else val,
                        "ref": ref, "err": err, "ok": err < 1e-9})
    return results


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_session19() -> Dict:
    stats = census_statistics(CENSUS)
    checks = spot_checks()
    n_ok = sum(1 for c in checks if c["ok"])

    classification_theorem_preview = {
        "EML_1_class": "All functions of form Re/Im(g(exp(ax+b))) for complex a,b and g linear",
        "EML_2_class": "Functions requiring one Log-then-exp composition (powers, arctan, log∘trig)",
        "EML_3_class": "Functions requiring sqrt and Log (arcsin, arccos) or nested Log",
        "EML_inf_class": "Functions defined by infinite processes (Gamma exact, Bessel, ζ, elliptic)",
    }

    return {
        "session": 19,
        "title": "Complex EML Depth Collapse Census",
        "census": CENSUS,
        "statistics": stats,
        "spot_checks": checks,
        "n_spot_checks_ok": n_ok,
        "n_spot_checks_total": len(checks),
        "classification_theorem_preview": classification_theorem_preview,
        "key_finding": (
            f"{stats['fraction_collapsible']} functions in the census are collapsible to finite depth. "
            f"{stats['euler_gateway_count']} use the Euler i-gateway. "
            "EML-∞ functions are those defined by infinite sums/products/integrals."
        ),
        "status": "PASS" if n_ok == len(checks) else f"PARTIAL ({n_ok}/{len(checks)})",
    }
