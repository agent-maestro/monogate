import json

def code_cell(src):
    return {"cell_type": "code", "source": src, "metadata": {}, "outputs": [], "execution_count": None}

def md_cell(src):
    return {"cell_type": "markdown", "source": src, "metadata": {}}

cells = []

cells.append(md_cell(
    "# EML Neural Network — Experiment 02\n"
    "**Complexity-Accuracy Pareto Frontier**\n\n"
    "The EML operator is `eml(x, y) = exp(x) − ln(y)`. Experiment 01 showed the network\n"
    "finds *some* EML construction — not necessarily the *minimal* one.\n\n"
    "Adding a complexity penalty `λ` to the loss:\n\n"
    "| Model | Penalty | Effect |\n"
    "|---|---|---|\n"
    "| `EMLTree(depth=2)` | `λ · Σ\\|leaf − 1\\|` | pulls leaves toward EML terminal `1` |\n"
    "| `EMLNetwork(depth=2)` | `λ · Σ\\|weight\\|` | pushes linear weights toward 0 (constant leaves) |\n\n"
    "**Three parts:**\n"
    "1. **Part A** — λ sweep for `EMLTree` targeting *e*: how does the formula change?\n"
    "2. **Part B** — λ sweep for `EMLNetwork` targeting `exp(x)`: Pareto frontier.\n"
    "3. **Part C** — Binary search for the critical λ where `EMLNetwork` snaps to minimal."
))

cells.append(code_cell(
    "import math\n"
    "import time\n"
    "\n"
    "import torch\n"
    "import matplotlib\n"
    "import matplotlib.pyplot as plt\n"
    "import numpy as np\n"
    "\n"
    "from monogate.network import EMLTree, EMLNetwork, fit\n"
    "\n"
    'matplotlib.rcParams.update({\n'
    '    "figure.facecolor": "#08090e",\n'
    '    "axes.facecolor":   "#0d0f18",\n'
    '    "axes.edgecolor":   "#1c1f2e",\n'
    '    "axes.labelcolor":  "#d4d4d4",\n'
    '    "text.color":       "#d4d4d4",\n'
    '    "xtick.color":      "#4a4d62",\n'
    '    "ytick.color":      "#4a4d62",\n'
    '    "grid.color":       "#1c1f2e",\n'
    '    "grid.linewidth":   0.5,\n'
    '    "lines.linewidth":  1.8,\n'
    '    "font.family":      "monospace",\n'
    '    "font.size":        10,\n'
    "})\n"
    'ORANGE = "#e8a020"\n'
    'BLUE   = "#6ab0f5"\n'
    'GREEN  = "#4ade80"\n'
    'RED    = "#f87171"\n'
    'MUTED  = "#4a4d62"\n'
    'CYAN   = "#67e8f9"\n'
    "\n"
    'print(f"torch {torch.__version__}  |  CPU only")'
))

cells.append(code_cell(
    "def best_of_n(model_fn, n=5, **fit_kwargs):\n"
    "    best_model, best_losses, best_loss = None, [], float('inf')\n"
    "    for seed in range(n):\n"
    "        torch.manual_seed(seed)\n"
    "        model = model_fn()\n"
    "        losses = fit(model, **fit_kwargs, log_every=0)\n"
    "        final = losses[-1] if losses else float('inf')\n"
    "        if final < best_loss:\n"
    "            best_model, best_losses, best_loss = model, losses, final\n"
    "    return best_model, best_losses\n"
    "\n"
    "def leaf_l1(model):\n"
    "    return sum((p - 1.0).abs().sum().item() for p in model.parameters())\n"
    "\n"
    "def weight_l1(model):\n"
    "    return sum(\n"
    "        p.abs().sum().item()\n"
    "        for name, p in model.named_parameters()\n"
    '        if "weight" in name\n'
    "    )\n"
    "\n"
    "def is_weight_sparse(model, tol=0.05):\n"
    "    return all(\n"
    "        p.abs().max().item() < tol\n"
    "        for name, p in model.named_parameters()\n"
    '        if "weight" in name\n'
    "    )\n"
    "\n"
    "LAMBDAS = [0, 0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 2.0]"
))

cells.append(md_cell(
    "---\n"
    "## Part A — EMLTree: λ sweep targeting *e*\n\n"
    "**Penalty:** `λ · Σ|leaf − 1|`\n\n"
    "At `λ=0` the network found `eml(eml(0.571, 1.349), eml(1.047, 0.875))` in experiment 01.\n"
    "As λ grows, leaves are pulled toward 1. At `depth=2`, setting all leaves to 1 gives\n"
    "`eml(eml(1,1), eml(1,1)) = eml(e, e) = exp(e) − 1 ≈ 14.78` — *not* e.\n\n"
    "This reveals that the leaf→1 penalty has the wrong inductive bias for depth=2:\n"
    "it eventually pushes the model **away** from the target."
))

cells.append(code_cell(
    "t0       = time.perf_counter()\n"
    "e_target = torch.tensor(math.e)\n"
    "\n"
    'rows_e = []\n'
    "print(f\"{'lambda':<10} {'|error|':<12} {'leaf_l1':<12} formula\")\n"
    'print("\u2500" * 80)\n'
    "for lam in LAMBDAS:\n"
    "    m, _ = best_of_n(\n"
    "        lambda: EMLTree(depth=2), n=5,\n"
    "        target=e_target, steps=3000, lr=0.05, lam=lam, loss_threshold=1e-9,\n"
    "    )\n"
    "    val   = m().item()\n"
    "    err   = abs(val - math.e)\n"
    "    cmplx = leaf_l1(m)\n"
    "    leaves = [p.item() for p in m.parameters()]\n"
    "    form  = m.formula()\n"
    "    rows_e.append({'lam': lam, 'error': err, 'complexity': cmplx,\n"
    "                   'leaves': leaves, 'formula': form})\n"
    "    print(f\"{lam:<10} {err:<12.3e} {cmplx:<12.4f} {form[:55]}\")\n"
    "\n"
    "print(f\"\\nPart A wall time: {time.perf_counter()-t0:.1f}s\")"
))

cells.append(md_cell(
    "---\n"
    "## Part B — EMLNetwork: Pareto frontier for exp(x)\n\n"
    "**Penalty:** `λ · Σ|weight|` (L1 on linear leaf weight matrices)\n\n"
    "Pushing weights toward 0 makes leaves behave as constants — simpler expressions.\n"
    "The right leaf for `exp(x) = eml(x, 1)` *should* be constant, so L1 on weights\n"
    "is the correct inductive bias here.\n\n"
    "**Pareto frontier:** x-axis = weight L1 (complexity), y-axis = normalised MSE."
))

cells.append(code_cell(
    "t0     = time.perf_counter()\n"
    "x2     = torch.linspace(0.1, 3.0, 100).unsqueeze(1)\n"
    "y2     = torch.exp(x2.squeeze())\n"
    "x2n    = (x2 - 0.1) / 2.9\n"
    "y2_max = y2.max().item()\n"
    "y2n    = y2 / y2_max\n"
    "\n"
    "rows_exp = []\n"
    "print(f\"{'lambda':<10} {'norm_mse':<14} {'weight_l1':<14} {'sparse?':<10} formula\")\n"
    "print(\"\u2500\" * 90)\n"
    "for lam in LAMBDAS:\n"
    "    m, losses = best_of_n(\n"
    "        lambda: EMLNetwork(in_features=1, depth=2), n=3,\n"
    "        x=x2n, y=y2n, steps=2000, lr=0.01, lam=lam, loss_threshold=1e-9,\n"
    "    )\n"
    "    norm_mse = losses[-1] if losses else float('nan')\n"
    "    cmplx    = weight_l1(m)\n"
    "    sparse   = is_weight_sparse(m, tol=0.05)\n"
    "    form     = m.formula(['x'])\n"
    "    rows_exp.append({'lam': lam, 'norm_mse': norm_mse, 'complexity': cmplx,\n"
    "                     'sparse': sparse, 'formula': form})\n"
    "    tag = 'SPARSE' if sparse else ''\n"
    "    print(f\"{lam:<10} {norm_mse:<14.3e} {cmplx:<14.4f} {tag:<10} {form[:45]}\")\n"
    "\n"
    "print(f\"\\nPart B wall time: {time.perf_counter()-t0:.1f}s\")"
))

cells.append(md_cell(
    "---\n"
    "## Part C — Binary search: critical λ for EMLNetwork\n\n"
    "Find the smallest λ where all leaf linear weights drop below 0.05 (effectively\n"
    "constant leaves = sparse formula). Reports the critical λ and the MSE cost of\n"
    "choosing the minimal-structure formula over the unconstrained fit."
))

cells.append(code_cell(
    "# Bracket from Part B\n"
    "lam_lo = max((r['lam'] for r in rows_exp if not r['sparse']), default=0.0)\n"
    "lam_hi = min((r['lam'] for r in rows_exp if r['sparse']),  default=LAMBDAS[-1])\n"
    "\n"
    "print(f'Bracket: [{lam_lo}, {lam_hi}]')\n"
    "if lam_lo >= lam_hi:\n"
    "    print('No sparse→dense transition in sweep.')\n"
    "    critical_lam = lam_hi\n"
    "else:\n"
    "    for i in range(14):\n"
    "        lam_mid = (lam_lo + lam_hi) / 2\n"
    "        torch.manual_seed(0)\n"
    "        m = EMLNetwork(in_features=1, depth=2)\n"
    "        fit(m, x=x2n, y=y2n, steps=3000, lr=0.01, lam=lam_mid,\n"
    "            log_every=0, loss_threshold=1e-9)\n"
    "        if is_weight_sparse(m, tol=0.05):\n"
    "            lam_hi = lam_mid\n"
    "        else:\n"
    "            lam_lo = lam_mid\n"
    "    critical_lam = (lam_lo + lam_hi) / 2\n"
    "\n"
    "# Evaluate at critical lambda\n"
    "torch.manual_seed(0)\n"
    "m_crit = EMLNetwork(in_features=1, depth=2)\n"
    "fit(m_crit, x=x2n, y=y2n, steps=3000, lr=0.01, lam=critical_lam,\n"
    "    log_every=0, loss_threshold=1e-9)\n"
    "with torch.no_grad():\n"
    "    pred_crit = m_crit(x2n).numpy() * y2_max\n"
    "norm_mse_crit = float(((torch.tensor(pred_crit) - y2)**2).mean()) / y2_max**2\n"
    "form_crit     = m_crit.formula(['x'])\n"
    "w_l1_crit     = weight_l1(m_crit)\n"
    "\n"
    "unconstrained_mse = rows_exp[0]['norm_mse']\n"
    "mse_cost          = norm_mse_crit - unconstrained_mse\n"
    "\n"
    "print(f'\\n' + '\u2500'*60)\n"
    "print(f'Critical lambda      : {critical_lam:.6f}')\n"
    "print(f'Formula              : {form_crit}')\n"
    "print(f'Weight L1 at crit.   : {w_l1_crit:.4f}')\n"
    "print(f'Norm MSE at crit.    : {norm_mse_crit:.3e}')\n"
    "print(f'')\n"
    "print(f'MSE cost of minimal structure vs unconstrained:')\n"
    "print(f'  lambda=0 norm MSE   : {unconstrained_mse:.3e}')\n"
    "print(f'  critical norm MSE   : {norm_mse_crit:.3e}')\n"
    "print(f'  increase            : {mse_cost/unconstrained_mse*100:.1f}%')"
))

cells.append(code_cell(
    "fig, axes = plt.subplots(1, 3, figsize=(15, 5))\n"
    "fig.suptitle('EML Complexity-Accuracy Pareto Frontier \u2014 Experiment 02',\n"
    "             color='#d4d4d4', fontsize=12, fontweight='bold', y=1.02)\n"
    "\n"
    "lams_a  = [r['lam'] for r in rows_e]\n"
    "errs_a  = [r['error'] for r in rows_e]\n"
    "cmplx_a = [r['complexity'] for r in rows_e]\n"
    "\n"
    "# Panel A: EMLTree error + leaf_l1 vs lambda\n"
    "ax  = axes[0]\n"
    "ax2 = ax.twinx()\n"
    "ax.semilogy(lams_a, errs_a,  'o-', color=ORANGE, linewidth=1.8, label='|error|')\n"
    "ax2.plot(lams_a, cmplx_a, 's--', color=BLUE, linewidth=1.4, label='leaf L1', alpha=0.8)\n"
    "ax.set_xlabel('lambda')\n"
    "ax.set_ylabel('|error|  (log scale)', color=ORANGE)\n"
    "ax2.set_ylabel('leaf L1  (complexity)', color=BLUE)\n"
    "ax.tick_params(axis='y', colors=ORANGE)\n"
    "ax2.tick_params(axis='y', colors=BLUE)\n"
    "ax.set_title('Part A \u00b7 EMLTree(depth=2) \u2192 e', color='#d4d4d4', fontsize=9)\n"
    "l1, lab1 = ax.get_legend_handles_labels()\n"
    "l2, lab2 = ax2.get_legend_handles_labels()\n"
    "ax.legend(l1+l2, lab1+lab2, fontsize=8)\n"
    "ax.grid(True)\n"
    "\n"
    "# Panel B: EMLNetwork Pareto frontier\n"
    "ax = axes[1]\n"
    "cmplx_b = [r['complexity'] for r in rows_exp]\n"
    "mse_b   = [r['norm_mse']   for r in rows_exp]\n"
    "lams_b  = [r['lam']        for r in rows_exp]\n"
    "colors  = [math.log10(l + 1e-4) for l in lams_b]\n"
    "sc = ax.scatter(cmplx_b, mse_b, c=colors, cmap='plasma', s=70, zorder=3)\n"
    "ax.plot(cmplx_b, mse_b, color=MUTED, linewidth=1.2, zorder=2)\n"
    "ax.axvline(w_l1_crit, color=CYAN, linestyle='--', linewidth=1.2,\n"
    "           label=f'critical \u03bb={critical_lam:.4f}')\n"
    "plt.colorbar(sc, ax=ax, label='log10(lambda)')\n"
    "ax.set_xlabel('weight L1 (complexity)')\n"
    "ax.set_ylabel('normalised MSE')\n"
    "ax.set_title('Part B \u00b7 EMLNetwork Pareto: exp(x)', color='#d4d4d4', fontsize=9)\n"
    "ax.legend(fontsize=8)\n"
    "ax.grid(True)\n"
    "\n"
    "# Panel C: leaf convergence (EMLTree)\n"
    "ax = axes[2]\n"
    "leaf_mat = np.array([r['leaves'] for r in rows_e])\n"
    "colors4  = [ORANGE, BLUE, GREEN, RED]\n"
    "for i in range(leaf_mat.shape[1]):\n"
    "    ax.plot(lams_a, leaf_mat[:, i], 'o-', color=colors4[i],\n"
    "            label=f'leaf {i+1}', linewidth=1.6)\n"
    "ax.axhline(1.0, color=MUTED, linestyle='--', linewidth=1.2, label='target = 1')\n"
    "ax.set_xlabel('lambda')\n"
    "ax.set_ylabel('leaf value')\n"
    "ax.set_title('Part C \u00b7 EMLTree leaf values vs \u03bb', color='#d4d4d4', fontsize=9)\n"
    "ax.legend(fontsize=8)\n"
    "ax.grid(True)\n"
    "\n"
    "plt.tight_layout()\n"
    "out_path = 'experiment_02_results.png'\n"
    "plt.savefig(out_path, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())\n"
    "print(f'Saved \u2192 {out_path}')\n"
    "plt.show()"
))

cells.append(code_cell(
    "print('\\n\u2500\u2500 Part A: EMLTree(depth=2) targeting e \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500')\n"
    "print(f\"{'lambda':<10} {'|error|':<12} {'leaf_l1':<12} formula\")\n"
    "print('\u2500' * 80)\n"
    "for r in rows_e:\n"
    "    print(f\"{r['lam']:<10} {r['error']:<12.3e} {r['complexity']:<12.4f} {r['formula'][:52]}\")\n"
    "\n"
    "print('\\n\u2500\u2500 Part B: EMLNetwork(depth=2) targeting exp(x) \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500')\n"
    "print(f\"{'lambda':<10} {'norm_mse':<14} {'weight_l1':<14} {'sparse':<8} formula\")\n"
    "print('\u2500' * 90)\n"
    "for r in rows_exp:\n"
    "    tag = '\u2713' if r['sparse'] else ''\n"
    "    print(f\"{r['lam']:<10} {r['norm_mse']:<14.3e} {r['complexity']:<14.4f} {tag:<8} {r['formula'][:42]}\")\n"
    "\n"
    "print(f'\\nCritical lambda (EMLNetwork): {critical_lam:.6f}')\n"
    "print(f'MSE cost of simplicity      : {mse_cost/unconstrained_mse*100:.1f}% increase in norm MSE')"
))

nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.11.0"},
    },
    "cells": cells,
}

with open("D:/monogate/python/notebooks/experiment_02.ipynb", "w", encoding="utf-8") as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("experiment_02.ipynb written.")
