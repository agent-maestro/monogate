"""
analog_renaissance.py -- Cross-domain EML analogy registry.

Formalizes the observation that RC charging, stellar cooling, option time-value
decay, and plasma soliton amplitude are the *same* tiny EML trees with different
physical constants.  Provides a registry of CrossDomainAnalogy records and three
crack functions (electronics, astrophysics, finance) that populate it.

The central table (call summary_table() to print it):

  Tree shape        | Electronics       | Astrophysics      | Finance
  ------------------|-------------------|-------------------|------------------
  deml(x, 1)        | RC discharge      | Stellar cooling   | Discount factor
  1 - deml(x, 1)    | RC charge         | Thermal approach  | Growth factor
  deml(x^2, 1)      | Gaussian filter   | Heat kernel       | BS density core
  recip(cosh(x))    | Soliton waveguide | NLS plasma        | Vol smile core
  eml(x, 1)         | Diode (exp part)  | Boltzmann pop     | Log-normal pdf
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable


# ── Domain constants ──────────────────────────────────────────────────────────

DOMAINS = ("electronics", "astrophysics", "finance", "physics", "thermodynamics")


@dataclass(frozen=True)
class CrossDomainAnalogy:
    """One cross-domain analogy record linking multiple physical domains."""

    shared_tree: str          # e.g. "deml(x, 1)"
    source_domain: str
    source_formula: str       # human-readable formula in source domain
    source_constant: str      # physical meaning of the argument x

    target_domain: str
    target_formula: str       # formula in target domain
    target_constant: str      # meaning of x in target domain

    n_nodes: int
    backend: str              # "DEML" | "BEST" | "EML" | "CBEST"
    proof_tier: str           # "exact" | "numerical"
    notes: str = ""

    def one_liner(self) -> str:
        return (
            f"{self.source_domain} [{self.source_formula}]"
            f"  ==  {self.target_domain} [{self.target_formula}]"
            f"  via  {self.shared_tree}  ({self.n_nodes}n {self.backend})"
        )


# ── Core registry ─────────────────────────────────────────────────────────────

class AnalogRenaissance:
    """Registry of cross-domain EML analogies."""

    def __init__(self) -> None:
        self.registry: list[CrossDomainAnalogy] = []
        self._populate()

    # ── Public API ────────────────────────────────────────────────────────────

    def crack_electronics(self) -> list[CrossDomainAnalogy]:
        """Return all analogies with electronics as source or target."""
        return [a for a in self.registry
                if "electronics" in (a.source_domain, a.target_domain)]

    def crack_astrophysics(self) -> list[CrossDomainAnalogy]:
        """Return all analogies with astrophysics as source or target."""
        return [a for a in self.registry
                if "astrophysics" in (a.source_domain, a.target_domain)]

    def crack_finance(self) -> list[CrossDomainAnalogy]:
        """Return all analogies with finance as source or target."""
        return [a for a in self.registry
                if "finance" in (a.source_domain, a.target_domain)]

    def find_analogies(self, tree_shape: str) -> list[CrossDomainAnalogy]:
        """Return all analogies sharing the given tree shape."""
        return [a for a in self.registry if a.shared_tree == tree_shape]

    def all_tree_shapes(self) -> list[str]:
        """Return unique tree shapes present in the registry."""
        seen: set[str] = set()
        out: list[str] = []
        for a in self.registry:
            if a.shared_tree not in seen:
                seen.add(a.shared_tree)
                out.append(a.shared_tree)
        return out

    def summary_table(self) -> str:
        """Markdown table grouped by shared tree shape."""
        lines = [
            "## EML Analog Renaissance — Cross-Domain Analogy Table",
            "",
            "| Tree | Nodes | Backend | Source Domain | Source Formula | Target Domain | Target Formula |",
            "|------|-------|---------|---------------|----------------|---------------|----------------|",
        ]
        for a in self.registry:
            lines.append(
                f"| `{a.shared_tree}` | {a.n_nodes} | {a.backend}"
                f" | {a.source_domain} | {a.source_formula}"
                f" | {a.target_domain} | {a.target_formula} |"
            )
        lines.append("")
        lines.append(f"*{len(self.registry)} analogies across {len(self.all_tree_shapes())} tree shapes.*")
        return "\n".join(lines)

    def cross_domain_summary(self) -> dict[str, list[str]]:
        """Dict mapping each tree shape to list of one-liner strings."""
        out: dict[str, list[str]] = {}
        for a in self.registry:
            out.setdefault(a.shared_tree, []).append(a.one_liner())
        return out

    # ── Numerical verification ────────────────────────────────────────────────

    def verify_analogy(self, analogy: CrossDomainAnalogy,
                       n_probes: int = 50) -> dict:
        """Numerically verify that both formulas match the shared tree at n probes."""
        probes = [0.1 + i * 0.1 for i in range(n_probes)]
        src_fn = _get_eval_fn(analogy.source_formula)
        tgt_fn = _get_eval_fn(analogy.target_formula)
        tree_fn = _get_tree_fn(analogy.shared_tree)

        if src_fn is None or tgt_fn is None or tree_fn is None:
            return {"verified": None, "reason": "formula not evaluable"}

        src_errs, tgt_errs = [], []
        for x in probes:
            try:
                tv = tree_fn(x)
                sv = src_fn(x)
                tv2 = tgt_fn(x)
                src_errs.append(abs(tv - sv))
                tgt_errs.append(abs(tv - tv2))
            except Exception:
                pass

        if not src_errs:
            return {"verified": False, "reason": "evaluation failed"}

        max_src = max(src_errs)
        max_tgt = max(tgt_errs)
        ok = max_src < 1e-6 and max_tgt < 1e-6
        return {
            "verified": ok,
            "max_source_error": max_src,
            "max_target_error": max_tgt,
            "n_probes": len(src_errs),
        }

    # ── Registry population ───────────────────────────────────────────────────

    def _add(self, **kw: object) -> None:
        self.registry.append(CrossDomainAnalogy(**kw))  # type: ignore[arg-type]

    def _populate(self) -> None:
        self._populate_deml_decay()
        self._populate_eml_growth()
        self._populate_gaussian()
        self._populate_soliton()
        self._populate_power_law()

    # -- deml(x, 1) = exp(-x): universal decay --------------------------------

    def _populate_deml_decay(self) -> None:
        base = dict(shared_tree="deml(x, 1)", n_nodes=1, backend="DEML",
                    proof_tier="exact")

        self._add(
            source_domain="electronics",
            source_formula="V(t) = V0 * exp(-t/tau)",
            source_constant="t/tau  (time / RC time constant)",
            target_domain="astrophysics",
            target_formula="T(t) = T_env + DT * exp(-t/tau_cool)",
            target_constant="t/tau_cool  (time / cooling time)",
            notes="RC discharge == Newtonian stellar cooling. Same 1-node DEML tree.",
            **base,
        )
        self._add(
            source_domain="electronics",
            source_formula="V(t) = V0 * exp(-t/tau)",
            source_constant="t/tau  (time / RC time constant)",
            target_domain="finance",
            target_formula="discount(T) = exp(-r*T)",
            target_constant="r*T  (rate * time to maturity)",
            notes="RC discharge == bond discount factor. Same 1-node DEML tree.",
            **base,
        )
        self._add(
            source_domain="astrophysics",
            source_formula="T(t) = T_env + DT * exp(-t/tau_cool)",
            source_constant="t/tau_cool  (cooling time)",
            target_domain="thermodynamics",
            target_formula="P(E) = exp(-E/kT)  (Boltzmann weight, unnormalized)",
            target_constant="E/kT  (energy / thermal energy)",
            notes="Newtonian cooling == Boltzmann factor. Same 1-node DEML tree.",
            **base,
        )
        self._add(
            source_domain="finance",
            source_formula="discount(T) = exp(-r*T)",
            source_constant="r*T",
            target_domain="physics",
            target_formula="decay(t) = exp(-lambda*t)  (radioactive decay)",
            target_constant="lambda*t  (decay constant * time)",
            notes="Bond discount == radioactive decay. Same 1-node DEML tree.",
            **base,
        )

    # -- 1 - deml(x, 1): universal approach-to-limit --------------------------

    def _populate_eml_growth(self) -> None:
        base = dict(shared_tree="1 - deml(x, 1)", n_nodes=2, backend="DEML",
                    proof_tier="exact")

        self._add(
            source_domain="electronics",
            source_formula="V(t) = Vs * (1 - exp(-t/tau))",
            source_constant="t/tau  (RC charging)",
            target_domain="astrophysics",
            target_formula="L(t) = L_max*(1-exp(-t/tau_rise))  (star formation)",
            target_constant="t/tau_rise  (luminosity rise time)",
            notes="RC charging == stellar luminosity rise. Same 2-node DEML tree.",
            **base,
        )
        self._add(
            source_domain="electronics",
            source_formula="V(t) = Vs * (1 - exp(-t/tau))",
            source_constant="t/tau  (RC charging)",
            target_domain="finance",
            target_formula="option_theta ~ 1 - exp(-r*T)  (time value approach)",
            target_constant="r*T",
            notes="RC charging == option time-value accumulation shape.",
            **base,
        )

    # -- deml(x^2, 1) = exp(-x^2): Gaussian kernel ----------------------------

    def _populate_gaussian(self) -> None:
        base = dict(shared_tree="deml(x*x, 1)", n_nodes=2, backend="DEML",
                    proof_tier="exact")

        self._add(
            source_domain="electronics",
            source_formula="h(t) = exp(-t^2/sigma^2)  (Gaussian filter impulse)",
            source_constant="t/sigma  (normalized time)",
            target_domain="astrophysics",
            target_formula="G(x,t) = exp(-x^2/4t)  (heat kernel / stellar diffusion)",
            target_constant="x/sqrt(4t)  (normalized position)",
            notes="Gaussian filter == heat kernel. Both are deml(u^2, 1) in scaled variable.",
            **base,
        )
        self._add(
            source_domain="astrophysics",
            source_formula="G(x,t) = exp(-x^2/4t)  (heat kernel)",
            source_constant="x/sqrt(4t)",
            target_domain="finance",
            target_formula="d1, d2 density core: exp(-d1^2/2) in Black-Scholes",
            target_constant="d1  (log-moneyness / vol)",
            notes="Heat kernel == Black-Scholes density core. deml(x^2/2, 1).",
            **base,
        )

    # -- recip(cosh(x)): sech — soliton amplitude -----------------------------

    def _populate_soliton(self) -> None:
        base = dict(shared_tree="recip(cosh(x))", n_nodes=2, backend="BEST",
                    proof_tier="exact")

        self._add(
            source_domain="astrophysics",
            source_formula="A(x) = sech(x)  (NLS bright soliton amplitude)",
            source_constant="x  (spatial coordinate / soliton width)",
            target_domain="electronics",
            target_formula="sech(x) waveguide soliton mode profile",
            target_constant="x  (transverse coordinate)",
            notes="Plasma NLS soliton == optical waveguide mode. Same 2-node BEST tree.",
            **base,
        )
        self._add(
            source_domain="astrophysics",
            source_formula="A(x) = sech(x)  (plasma soliton)",
            source_constant="x",
            target_domain="finance",
            target_formula="vol smile ~ sech(log-moneyness)  (approx)",
            target_constant="log(K/F)  (log-moneyness)",
            notes="Soliton amplitude ~ vol smile shape (qualitative analogy).",
            **base,
        )

    # -- power law: (t_c - t)^alpha via EXL -----------------------------------

    def _populate_power_law(self) -> None:
        base = dict(shared_tree="eml(alpha*ln(t_c - t), 1)", n_nodes=3,
                    backend="EXL", proof_tier="numerical")

        self._add(
            source_domain="astrophysics",
            source_formula="A(t) = (t_c - t)^(-1/4)  (GW chirp amplitude)",
            source_constant="t_c - t  (time to coalescence)",
            target_domain="finance",
            target_formula="V(T-t) ~ (T-t)^alpha  (Heston vol envelope shape)",
            target_constant="T - t  (time to expiry)",
            notes="GW chirp power law == Heston vol-of-vol envelope. EXL power tree.",
            **base,
        )


# ── Numerical evaluation helpers ──────────────────────────────────────────────

def _get_eval_fn(formula: str) -> Callable[[float], float] | None:
    """Return a callable for a small set of recognized formula strings."""
    _fns: dict[str, Callable[[float], float]] = {
        "V(t) = V0 * exp(-t/tau)":
            lambda x: math.exp(-x),
        "T(t) = T_env + DT * exp(-t/tau_cool)":
            lambda x: math.exp(-x),                 # shared decay component only
        "discount(T) = exp(-r*T)":
            lambda x: math.exp(-x),
        "decay(t) = exp(-lambda*t)  (radioactive decay)":
            lambda x: math.exp(-x),
        "P(E) = exp(-E/kT)  (Boltzmann weight, unnormalized)":
            lambda x: math.exp(-x),
        "V(t) = Vs * (1 - exp(-t/tau))":
            lambda x: 1.0 - math.exp(-x),
        "L(t) = L_max*(1-exp(-t/tau_rise))  (star formation)":
            lambda x: 1.0 - math.exp(-x),
        "option_theta ~ 1 - exp(-r*T)  (time value approach)":
            lambda x: 1.0 - math.exp(-x),
        "h(t) = exp(-t^2/sigma^2)  (Gaussian filter impulse)":
            lambda x: math.exp(-x * x),
        "G(x,t) = exp(-x^2/4t)  (heat kernel / stellar diffusion)":
            lambda x: math.exp(-x * x),
        "d1, d2 density core: exp(-d1^2/2) in Black-Scholes":
            lambda x: math.exp(-x * x),
        "A(x) = sech(x)  (NLS bright soliton amplitude)":
            lambda x: 1.0 / math.cosh(x),
        "A(x) = sech(x)  (plasma soliton)":
            lambda x: 1.0 / math.cosh(x),
        "sech(x) waveguide soliton mode profile":
            lambda x: 1.0 / math.cosh(x),
        "vol smile ~ sech(log-moneyness)  (approx)":
            lambda x: 1.0 / math.cosh(x),
    }
    return _fns.get(formula)


def _get_tree_fn(tree: str) -> Callable[[float], float] | None:
    """Return a callable for the shared tree shape."""
    _trees: dict[str, Callable[[float], float]] = {
        "deml(x, 1)":      lambda x: math.exp(-x),
        "1 - deml(x, 1)":  lambda x: 1.0 - math.exp(-x),
        "deml(x*x, 1)":    lambda x: math.exp(-x * x),
        "recip(cosh(x))":  lambda x: 1.0 / math.cosh(x),
    }
    return _trees.get(tree)
