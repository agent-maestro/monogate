# EMLProverV2 — Advanced Theorem Proving

`EMLProverV2` extends `EMLProver` with three new capabilities:
conjecture generation, proof compression, and visualization.

## Installation

```bash
pip install monogate
# Optional for visualization:
pip install matplotlib networkx
```

## Quick Start

```python
from monogate import EMLProverV2

p = EMLProverV2(n_probe=500)

# Prove a standard identity
result = p.prove("sin(x)**2 + cos(x)**2 == 1")
print(result.status)   # "proved_numerical"
print(result.proved()) # True
```

## Conjecture Generation

Generate novel mathematical conjectures by mutating known catalog identities:

```python
conjectures = p.generate_conjectures(category="trig", n=10, seed=42)
for c in conjectures:
    print(c.name, c.expression)
```

**Algorithm**: For each seed identity in the requested category, five
grammar mutations are applied (x→2x, x→x/2, negation, ×2, ×1/2). Each
candidate is numerically verified (500 points, tolerance 1e-6) and
deduplicated against the existing catalog.

**Parameters**:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `category` | `"trig"` | Category alias: `"trig"`, `"hyperbolic"`, `"exponential"`, `"special"`, `"physics"`, `"eml"`, `"open"` |
| `n` | `20` | Maximum number of conjectures to return |
| `difficulty` | `"medium"` | Difficulty tag for generated identities |
| `seed` | `42` | Random seed for reproducibility |

## Proof Compression

Minimize the EML witness tree while preserving the proof:

```python
result = p.prove("exp(x) - log(1) == exp(x)")
compressed = p.compress_proof(result, n_simulations=500)

print(f"Original nodes: {result.node_count}")
print(f"Compressed nodes: {compressed.node_count}")
```

**Algorithm**: Starting from the witness tree (size $n$), calls `minimax_eml`
with budget $n-1, n-2, \ldots$ until no shorter equivalent tree achieves
$L^\infty < 10^{-10}$. Returns the shortest valid witness found.

## Proof Visualization

Render the EML witness tree as a matplotlib figure:

```python
import matplotlib
matplotlib.use("Agg")  # or "TkAgg" for interactive

result = p.prove("sin(x)**2 + cos(x)**2 == 1")
p.visualize_proof(result, style="tree", output_path="proof.png")
```

**Styles**:

| Style | Description |
|-------|-------------|
| `"tree"` | Top-down hierarchical layout |
| `"radial"` | Circular layout with root at center |
| `"step"` | Side-by-side LHS/RHS trees with proof method label |

**Node colors**:
- `cornflowerblue` — EML internal nodes (`eml(·,·)`)
- `lightgreen` — constant leaves (e.g., `1.0`, `2.0`)
- `coral` — variable leaf (`x`)

## Batch Proving

Prove multiple identities in one call, with progress display:

```python
from monogate import ALL_IDENTITIES

# Prove all trivial identities
trivial = [i for i in ALL_IDENTITIES if i.difficulty == "trivial"]
report = p.batch_prove(trivial, show_progress=True)

print(f"Success rate: {report.success_rate:.1%}")
print(f"Proved: {report.n_proved}/{report.n_total}")
```

`batch_prove` accepts both `Identity` objects and plain expression strings:

```python
report = p.batch_prove([
    "exp(x) == exp(x)",
    "sin(x)**2 + cos(x)**2 == 1",
    "log(exp(x)) == x",
])
```

## Identity Catalog (120+)

The `ALL_IDENTITIES` catalog contains 120+ identities across 7 categories:

```python
from monogate import ALL_IDENTITIES, get_by_category, get_by_difficulty

# By category
trig_ids = get_by_category("trigonometric")   # 27 identities
hyp_ids  = get_by_category("hyperbolic")      # 20 identities

# By difficulty
easy = get_by_difficulty("trivial")           # Trivial identities
hard = get_by_difficulty("hard")              # Hard identities
open_problems = get_by_difficulty("open")     # Open conjectures

print(f"Total: {len(ALL_IDENTITIES)}")
```

## API Reference

### `EMLProverV2`

```python
class EMLProverV2(EMLProver):
    def generate_conjectures(
        self,
        category: str = "trig",
        n: int = 20,
        difficulty: str = "medium",
        seed: int = 42,
    ) -> list[Identity]: ...

    def compress_proof(
        self,
        result: ProofResult,
        n_simulations: int = 2000,
        seed: int = 42,
    ) -> ProofResult: ...

    def visualize_proof(
        self,
        result: ProofResult,
        style: str = "tree",
        output_path: str | None = None,
    ) -> None: ...

    def batch_prove(
        self,
        catalog_slice: list[Identity] | list[str],
        show_progress: bool = True,
        **kwargs,
    ) -> BenchmarkReport: ...
```

All `EMLProver` methods (`prove`, `prove_batch`, `benchmark`) are inherited.
