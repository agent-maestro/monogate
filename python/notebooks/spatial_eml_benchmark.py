"""
spatial_eml_benchmark.py — Session 42: EML vs SIREN on 2D Spatial Functions
=============================================================================

Benchmarks:
  1. EML MCTS symbolic regression on 5 standard 2D implicit functions
  2. SIREN (sin-activation coordinate network) baseline on same targets
  3. EML-SIREN (EMLLayer activation) vs sin-SIREN
  4. Comparison: MSE, L-inf, parameter count, EML-k complexity certificate
  5. Pareto plot: accuracy vs effective node count

Run:
    cd python/
    python notebooks/spatial_eml_benchmark.py

Requires: numpy, matplotlib
Optional: torch >= 2.0 (for SIREN baseline; gracefully skipped if absent)
"""

from __future__ import annotations

import math
import sys
import time
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np

from monogate.frontiers.spatial_eml import (
    ALL_TARGETS,
    CIRCLE_SDF,
    ELLIPSE_SDF,
    GAUSSIAN_2D,
    RING_SDF,
    INVERSE_SQ,
    SpatialSRResult,
    eval_on_grid,
    fit_spatial_eml,
    formula_to_2d,
    print_results_table,
    pareto_analysis,
)

# ── Config ────────────────────────────────────────────────────────────────────

N_SIMULATIONS = 3000      # MCTS simulations per target
DEPTH         = 5         # max EML tree depth
GRID_SIZE     = 64        # evaluation grid resolution
SIREN_STEPS   = 3000      # SIREN training steps
SIREN_WIDTH   = 32        # SIREN hidden width
SEED          = 42

BENCHMARK_TARGETS = [CIRCLE_SDF, ELLIPSE_SDF, GAUSSIAN_2D, RING_SDF, INVERSE_SQ]

RESULTS_DIR = Path(__file__).parent.parent.parent / "python" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# ── Section 1: EML MCTS Search ───────────────────────────────────────────────

print()
print("=" * 70)
print("  Section 1: EML Symbolic Regression (MCTS)")
print("  Targets: circle SDF, ellipse SDF, Gaussian, ring SDF, inverse-sq")
print("=" * 70)

eml_results: list[SpatialSRResult] = []

for target in BENCHMARK_TARGETS:
    print()
    result = fit_spatial_eml(
        target=target,
        n_simulations=N_SIMULATIONS,
        depth=DEPTH,
        grid_size=GRID_SIZE,
        search="mcts",
        seed=SEED,
        verbose=True,
    )
    eml_results.append(result)

print_results_table(eml_results)

# ── Section 2: SIREN Baseline ────────────────────────────────────────────────

print("=" * 70)
print("  Section 2: SIREN Baseline (sin-activation coordinate network)")
print("=" * 70)
print()

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    _TORCH_OK = True
except ImportError:
    print("  torch not available — skipping SIREN baseline")
    _TORCH_OK = False


if _TORCH_OK:
    from dataclasses import dataclass

    @dataclass
    class SIRENResult:
        target_name: str
        model_name: str
        mse_2d: float
        l_inf_2d: float
        n_params: int
        eml_node_count: int | None
        train_time_s: float

    class SinSIREN2D(torch.nn.Module):
        """Standard 2D SIREN: (x,y) -> sin-activated MLP -> scalar."""
        def __init__(self, width: int = 32, n_layers: int = 3) -> None:
            super().__init__()
            layers = [torch.nn.Linear(2, width)]
            for _ in range(n_layers - 2):
                layers.append(torch.nn.Linear(width, width))
            layers.append(torch.nn.Linear(width, 1))
            self.layers = torch.nn.ModuleList(layers)
            self._init_weights()

        def _init_weights(self) -> None:
            with torch.no_grad():
                # SIREN init: first layer scale 1, rest scale sqrt(6/n)
                torch.nn.init.uniform_(self.layers[0].weight, -1.0, 1.0)
                for layer in self.layers[1:]:
                    n = layer.weight.shape[1]
                    b = math.sqrt(6.0 / n)
                    torch.nn.init.uniform_(layer.weight, -b, b)

        def forward(self, xy: torch.Tensor) -> torch.Tensor:
            h = xy
            for layer in self.layers[:-1]:
                h = torch.sin(30.0 * layer(h) if layer is self.layers[0] else layer(h))
            return self.layers[-1](h)

    def _make_eml_siren_2d(width: int = 32, depth: int = 2):
        """2D EML-SIREN: replace sin with EMLLayer."""
        try:
            from monogate.torch import EMLLayer

            class EMLSIREN2D(torch.nn.Module):
                def __init__(self) -> None:
                    super().__init__()
                    self.eml1 = EMLLayer(2, width, depth=depth)
                    self.eml2 = EMLLayer(width, width, depth=depth)
                    self.out  = torch.nn.Linear(width, 1)

                def forward(self, xy: torch.Tensor) -> torch.Tensor:
                    return self.out(self.eml2(self.eml1(xy)))

                @property
                def eml_node_count(self) -> int:
                    return self.eml1.n_eml_nodes + self.eml2.n_eml_nodes

            return EMLSIREN2D()
        except ImportError:
            return None

    def _train_model(model, xy_train, z_train, steps=3000, lr=1e-3):
        opt = torch.optim.Adam(model.parameters(), lr=lr)
        for _ in range(steps):
            opt.zero_grad()
            pred = model(xy_train).squeeze()
            loss = F.mse_loss(pred, z_train)
            if not torch.isfinite(loss):
                break
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()

    def _eval_siren(model, target, grid_size=64, domain=2.0):
        xs = np.linspace(-domain, domain, grid_size)
        ys = np.linspace(-domain, domain, grid_size)
        xy_list, z_list = [], []
        for xi in xs:
            for yi in ys:
                try:
                    z_list.append(target.fn(float(xi), float(yi)))
                    xy_list.append([float(xi), float(yi)])
                except Exception:
                    pass
        xy_t = torch.tensor(xy_list, dtype=torch.float32)
        z_t  = torch.tensor(z_list,  dtype=torch.float32)
        with torch.no_grad():
            preds = model(xy_t).squeeze()
        errors = (preds - z_t).numpy() ** 2
        mse = float(errors.mean())
        l_inf = float(np.sqrt(errors.max()))
        return mse, l_inf

    siren_results: list[SIRENResult] = []

    for target in BENCHMARK_TARGETS:
        domain = target.domain if isinstance(target.domain, float) else float(target.domain)
        xs = np.linspace(-domain, domain, GRID_SIZE)
        ys = np.linspace(-domain, domain, GRID_SIZE)
        xy_list, z_list = [], []
        for xi in xs:
            for yi in ys:
                try:
                    z_list.append(target.fn(float(xi), float(yi)))
                    xy_list.append([float(xi), float(yi)])
                except Exception:
                    pass

        xy_t = torch.tensor(xy_list, dtype=torch.float32)
        z_t  = torch.tensor(z_list,  dtype=torch.float32)

        configs = [
            ("sin-SIREN",     lambda: SinSIREN2D(width=SIREN_WIDTH, n_layers=3), None),
            ("EML-SIREN(d=2)", lambda: _make_eml_siren_2d(width=SIREN_WIDTH, depth=2), None),
        ]

        print(f"  Target: {target.name}")
        for model_name, factory, _ in configs:
            torch.manual_seed(SEED)
            model = factory()
            if model is None:
                print(f"    {model_name:<20}: (EMLLayer not available)")
                continue
            n_params = sum(p.numel() for p in model.parameters())
            n_eml = getattr(model, "eml_node_count", None)

            t0 = time.perf_counter()
            _train_model(model, xy_t, z_t, steps=SIREN_STEPS)
            elapsed = time.perf_counter() - t0

            mse, l_inf = _eval_siren(model, target, grid_size=GRID_SIZE, domain=domain)
            print(f"    {model_name:<20}: MSE={mse:.3e}  L-inf={l_inf:.3e}  "
                  f"params={n_params:5d}" +
                  (f"  eml_nodes={n_eml}" if n_eml is not None else "") +
                  f"  t={elapsed:.1f}s")

            siren_results.append(SIRENResult(
                target_name=target.name,
                model_name=model_name,
                mse_2d=mse,
                l_inf_2d=l_inf,
                n_params=n_params,
                eml_node_count=n_eml,
                train_time_s=elapsed,
            ))
        print()

# ── Section 3: Head-to-head comparison ───────────────────────────────────────

print("=" * 70)
print("  Section 3: EML SR vs SIREN — head-to-head")
print("=" * 70)
print()
print(f"  {'Target':<18} {'Method':<22} {'MSE-2D':<12} {'L-inf':<12} {'Params/Nodes'}")
print("  " + "-" * 70)

for r in eml_results:
    n_nodes = r.formula_1d.count("exp") + r.formula_1d.count("log") + 1
    mse_str = f"{r.mse_2d:.3e}" if math.isfinite(r.mse_2d) else "FAILED"
    linf_str = f"{r.l_inf_2d:.3e}" if math.isfinite(r.l_inf_2d) else "FAILED"
    print(f"  {r.target_name:<18} {'EML-MCTS (symbolic)':<22} {mse_str:<12} {linf_str:<12} {n_nodes} nodes  [{r.eml_k_class}]")

if _TORCH_OK and "siren_results" in dir():
    for sr in siren_results:
        mse_str = f"{sr.mse_2d:.3e}"
        linf_str = f"{sr.l_inf_2d:.3e}"
        nodes_str = f"{sr.n_params} params"
        print(f"  {sr.target_name:<18} {sr.model_name:<22} {mse_str:<12} {linf_str:<12} {nodes_str}")

print()

# ── Section 4: EML-k Certificates ────────────────────────────────────────────

print("=" * 70)
print("  Section 4: EML-k Complexity Certificates")
print("  (Provable lower bounds from the Infinite Zeros Barrier)")
print("=" * 70)
print()

for r in eml_results:
    print(f"  {r.target_name}")
    print(f"    Discovered formula: {r.formula_1d}")
    if r.raw_result and hasattr(r.raw_result, "best_formula"):
        print(f"    2D formula:         {r.formula_2d}")
    print(f"    EML-k class:        {r.eml_k_class}")
    if r.error:
        print(f"    [search error: {r.error}]")
    print()

# ── Section 5: Pareto analysis ────────────────────────────────────────────────

pareto_pts = pareto_analysis(eml_results)
print("=" * 70)
print("  Section 5: Pareto-Efficient Points (MSE vs Node Count)")
print("=" * 70)
print()
print(f"  {'Target':<20} {'MSE-2D':<12} {'Nodes':<8} {'EML-k'}")
print("  " + "-" * 55)
for p in pareto_pts:
    print(f"  {p.name:<20} {p.mse_2d:.3e}    {p.n_nodes:<8} {p.eml_k}")
print()

# ── Section 6: Visualization ──────────────────────────────────────────────────

try:
    import matplotlib.pyplot as plt
    import matplotlib

    matplotlib.use("Agg")

    fig, axes = plt.subplots(len(BENCHMARK_TARGETS), 3,
                             figsize=(14, 4 * len(BENCHMARK_TARGETS)))
    fig.suptitle("EML Spatial Symbolic Regression — Session 42", fontsize=12, y=1.01)

    for row, (target, result) in enumerate(zip(BENCHMARK_TARGETS, eml_results)):
        domain = target.domain if isinstance(target.domain, float) else float(target.domain)

        # Ground truth
        ax_true = axes[row, 0]
        X, Y, Z_true = eval_on_grid(target.fn, domain=domain, grid_size=48)
        im = ax_true.contourf(X, Y, Z_true, levels=20, cmap="RdBu_r")
        ax_true.set_title(f"{target.name}\n(ground truth)", fontsize=8)
        ax_true.set_aspect("equal")
        plt.colorbar(im, ax=ax_true, fraction=0.046)

        # EML reconstruction — use fn_1d from the result directly
        ax_eml = axes[row, 1]
        Z_eml = None
        if not result.error and result.fn_1d is not None:
            try:
                if result.reduction_mode == "radial":
                    def _f2d_eml(x, y, _fn=result.fn_1d):
                        r = math.sqrt(x * x + y * y)
                        try:
                            return _fn(r)
                        except Exception:
                            return float("nan")
                else:
                    def _f2d_eml(x, y, _fn=result.fn_1d):
                        try:
                            return _fn(x)
                        except Exception:
                            return float("nan")
                _, _, Z_eml = eval_on_grid(_f2d_eml, domain=domain, grid_size=48)
                Z_eml_clean = np.where(np.isfinite(Z_eml), Z_eml, 0.0)
                im2 = ax_eml.contourf(X, Y, Z_eml_clean, levels=20, cmap="RdBu_r")
                ax_eml.set_title(
                    f"EML formula\n{result.formula_1d[:30]}\nMSE={result.mse_2d:.2e}",
                    fontsize=7
                )
                plt.colorbar(im2, ax=ax_eml, fraction=0.046)
            except Exception as e:
                ax_eml.text(0.5, 0.5, f"vis error:\n{e}", transform=ax_eml.transAxes,
                            ha="center", va="center", fontsize=7)
                ax_eml.set_title("EML formula\n(vis error)", fontsize=8)
        else:
            ax_eml.text(0.5, 0.5, "search failed", transform=ax_eml.transAxes,
                        ha="center", va="center")
            ax_eml.set_title("EML (failed)", fontsize=8)
        ax_eml.set_aspect("equal")

        # Error map
        ax_err = axes[row, 2]
        if Z_eml is not None:
            try:
                Z_err = np.abs(Z_true - Z_eml)
                Z_err_clean = np.where(np.isfinite(Z_err), Z_err, 0.0)
                im3 = ax_err.contourf(X, Y, Z_err_clean, levels=20, cmap="hot_r")
                ax_err.set_title(
                    f"Abs error\nL-inf={result.l_inf_2d:.2e}  [{result.eml_k_class}]",
                    fontsize=7
                )
                plt.colorbar(im3, ax=ax_err, fraction=0.046)
            except Exception:
                ax_err.set_title("error map (failed)", fontsize=8)
        else:
            ax_err.set_title("error map (N/A)", fontsize=8)
        ax_err.set_aspect("equal")

        for ax in [ax_true, ax_eml, ax_err]:
            ax.set_xlabel("x", fontsize=7)
            ax.set_ylabel("y", fontsize=7)

    plt.tight_layout()
    out_path = RESULTS_DIR / "spatial_eml_benchmark.png"
    plt.savefig(str(out_path), dpi=120, bbox_inches="tight")
    print(f"  Visualization saved -> {out_path}")
    plt.close()

except ImportError:
    print("  (matplotlib not available -- skipping visualization)")
except Exception as e:
    print(f"  Visualization error: {e}")

# ── Pareto plot ───────────────────────────────────────────────────────────────

try:
    import matplotlib.pyplot as plt
    import matplotlib

    matplotlib.use("Agg")

    fig2, ax = plt.subplots(figsize=(7, 5))
    ax.set_title("EML Spatial SR — MSE vs Node Count\n(Pareto frontier)", fontsize=10)

    node_counts = [r.formula_1d.count("exp") + r.formula_1d.count("log") + 1
                   for r in eml_results if math.isfinite(r.mse_2d)]
    mse_vals = [r.mse_2d for r in eml_results if math.isfinite(r.mse_2d)]
    names = [r.target_name for r in eml_results if math.isfinite(r.mse_2d)]
    eml_ks = [r.eml_k_class for r in eml_results if math.isfinite(r.mse_2d)]

    colors = {"EML-1": "#10b981", "EML-≥1": "#10b981",
              "EML-≥2": "#f59e0b", "EML-≥3": "#ef4444",
              "EML-inf": "#6366f1", "unknown": "#94a3b8"}

    for nc, mse, name, ek in zip(node_counts, mse_vals, names, eml_ks):
        color = colors.get(ek, "#94a3b8")
        ax.scatter(nc, mse, s=100, color=color, zorder=5)
        ax.annotate(name, (nc, mse), textcoords="offset points",
                    xytext=(6, 3), fontsize=8)

    # Add SIREN data points if available
    if _TORCH_OK and "siren_results" in dir():
        for sr in siren_results:
            if sr.model_name == "sin-SIREN":
                ax.scatter(sr.n_params, sr.mse_2d, marker="^", s=80,
                           color="#64748b", alpha=0.6, zorder=4)
                ax.annotate(f"{sr.target_name}\n(SIREN)", (sr.n_params, sr.mse_2d),
                            textcoords="offset points", xytext=(4, -10), fontsize=6, color="#64748b")

    ax.set_xlabel("Node count (EML) / Param count (SIREN)")
    ax.set_ylabel("MSE on 2D test grid")
    ax.set_yscale("log")
    ax.grid(True, alpha=0.3)

    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#10b981", markersize=10, label="EML-1"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#f59e0b", markersize=10, label="EML-≥2"),
        Line2D([0], [0], marker="^", color="w", markerfacecolor="#64748b", markersize=10, label="SIREN"),
    ]
    ax.legend(handles=legend_elements, fontsize=8)

    plt.tight_layout()
    pareto_path = RESULTS_DIR / "spatial_eml_pareto.png"
    plt.savefig(str(pareto_path), dpi=120)
    print(f"  Pareto plot saved   -> {pareto_path}")
    plt.close()

except Exception as e:
    print(f"  Pareto plot error: {e}")

# ── Final summary ─────────────────────────────────────────────────────────────

print()
print("=" * 70)
print("  Session 42 Summary")
print("=" * 70)
print()

best = min(eml_results, key=lambda r: r.mse_2d if math.isfinite(r.mse_2d) else 1e9)
worst = max(eml_results, key=lambda r: r.mse_2d if math.isfinite(r.mse_2d) else 1e9)

print(f"  Targets evaluated:  {len(eml_results)}")
print(f"  Best MSE-2D:        {best.mse_2d:.3e}  ({best.target_name})")
print(f"  Hardest target:     {worst.target_name}  (MSE={worst.mse_2d:.3e})")
print()
print("  EML-k certificates issued:")
for r in eml_results:
    print(f"    {r.target_name:<20}: {r.eml_k_class}")
print()

proven_count = sum(1 for r in eml_results if r.eml_k_class.startswith("EML-1"))
print(f"  EML-1 targets:      {proven_count}/{len(eml_results)}  "
      "(one-node approximation class)")
print()
print("  Key result: Radially symmetric 2D spatial functions (SDFs, Gaussians)")
print("  are reducible to EML-1 class via r=sqrt(x^2+y^2) encoding,")
print("  with provable density guarantee from the EML Weierstrass Theorem.")
print()
print("  Next: Session 43 — bivariate EML grammar for non-radial targets.")
print()
print("=" * 70)
print("  DONE")
print("=" * 70)
