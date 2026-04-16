# EML Neural Architecture Search

`monogate.nas` provides evolutionary search for novel activation functions
over the EML grammar.

## Installation

```bash
pip install monogate numpy
```

## Quick Start

```python
import numpy as np
from monogate.nas import EMLActivationSearch, complexity_penalized_fitness

# Generate some regression data
X = np.linspace(-2, 2, 100).reshape(-1, 1)
y = X.ravel() ** 2 + np.sin(X.ravel())

# Search for best EML activation
nas = EMLActivationSearch(max_depth=4, population_size=30, seed=42)
result = nas.search_for_activation(X, y, n_generations=20, alpha=0.01)

print(f"Best formula: {result.best_formula}")
print(f"MSE: {result.fitness:.6f}")
print(f"EML nodes: {result.n_nodes}")
```

## Custom Fitness Function

Supply any callable `(tree_dict) → float` (lower = better):

```python
def my_fitness(tree):
    preds = eval_my_tree(tree, X)
    return float(np.mean((preds - y) ** 2)) + 0.05 * tree_size(tree)

result = nas.search(my_fitness, n_generations=50, log_every=10)
```

## Comparing Against Baselines

```python
comparison = nas.compare_activations(result.best_tree, X, y)
for name, mse in sorted(comparison.items(), key=lambda x: x[1]):
    print(f"  {name:15s}  MSE={mse:.6f}")
```

Output:
```
  eml_discovered   MSE=0.012345
  silu             MSE=0.023456
  gelu             MSE=0.025678
  tanh             MSE=0.041234
  relu             MSE=0.087654
  elu              MSE=0.092345
  sigmoid          MSE=0.156789
```

## Fitness Functions

### `regression_fitness`

```python
from monogate.nas import regression_fitness

mse = regression_fitness(tree_dict, X, y)
```

Mean squared error of the EML tree evaluated on $(X, y)$.

### `complexity_penalized_fitness`

```python
from monogate.nas import complexity_penalized_fitness

score = complexity_penalized_fitness(tree_dict, X, y, alpha=0.01)
# score = MSE + alpha * n_eml_nodes
```

Pareto trade-off between accuracy and parsimony.  Increase `alpha` for
simpler trees; decrease for higher accuracy.

## Evolution Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_depth` | `4` | Maximum EML tree depth |
| `population_size` | `50` | Individuals per generation |
| `mutation_rate` | `0.3` | Probability of mutating a child |
| `crossover_rate` | `0.2` | Probability of crossover between parents |
| `seed` | `42` | Random seed |

## NASResult

```python
@dataclass(frozen=True)
class NASResult:
    best_tree: dict        # Winning EML tree dict
    best_formula: str      # Human-readable formula
    fitness: float         # Best fitness (lower = better)
    n_nodes: int           # EML internal node count
    generation: int        # Generation where best was found
    elapsed_s: float       # Wall-clock time
    history: list[tuple]   # (generation, best_fitness) checkpoints
```

Access the history to plot evolution curves:

```python
import matplotlib.pyplot as plt

gens, fits = zip(*result.history)
plt.plot(gens, fits)
plt.xlabel("Generation")
plt.ylabel("Fitness")
plt.title(f"EML NAS: {result.best_formula}")
plt.savefig("nas_evolution.png")
```

## API Reference

```python
class EMLActivationSearch:
    def __init__(
        self,
        max_depth: int = 4,
        population_size: int = 50,
        mutation_rate: float = 0.3,
        crossover_rate: float = 0.2,
        seed: int = 42,
    ) -> None: ...

    def search(
        self,
        fitness_fn: Callable[[dict], float],
        n_generations: int = 20,
        log_every: int = 5,
    ) -> NASResult: ...

    def search_for_activation(
        self,
        X: np.ndarray,
        y: np.ndarray,
        n_generations: int = 20,
        alpha: float = 0.01,
        log_every: int = 5,
    ) -> NASResult: ...

    def compare_activations(
        self,
        discovered_tree: dict,
        X: np.ndarray,
        y: np.ndarray,
        baselines: list[str] | None = None,
    ) -> dict[str, float]: ...
```
