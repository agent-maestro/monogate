"""
monogate.neural_scorer — Feature-based neural scorer for EML proof search.

Provides a small MLP that scores EML trees by their "promise" — the
likelihood that the tree leads to a short, correct proof.  Trained online
from successful witness proofs (reward = 1 / (1 + node_count)).

The forward pass is pure numpy (no torch dependency at inference time).
Torch is used only during the training step and is imported lazily.

Public API
----------
extract_tree_features      — 12 hand-crafted features from an EML tree dict
FeatureBasedEMLScorer      — MLP scorer with online training and persistence
ExperienceBuffer           — bounded deque of (features, reward) pairs
"""

from __future__ import annotations

import json
import math
import os
from collections import deque
from dataclasses import dataclass, field
from typing import Deque, List, Optional, Tuple

import numpy as np

__all__ = [
    "extract_tree_features",
    "FeatureBasedEMLScorer",
    "ExperienceBuffer",
    "N_FEATURES",
]

# Number of features extracted from each tree
N_FEATURES: int = 12


# ── Tree feature extraction ───────────────────────────────────────────────────

def _tree_depth(tree: dict) -> int:
    """Maximum depth of an EML tree (leaves = 0)."""
    if tree["op"] != "eml":
        return 0
    return 1 + max(_tree_depth(tree["left"]), _tree_depth(tree["right"]))


def _count_eml_nodes(tree: dict) -> int:
    """Count internal EML nodes (not leaves)."""
    if tree["op"] != "eml":
        return 0
    return 1 + _count_eml_nodes(tree["left"]) + _count_eml_nodes(tree["right"])


def _count_total(tree: dict) -> int:
    """Count all nodes (leaves + internal)."""
    if tree["op"] != "eml":
        return 1
    return 1 + _count_total(tree["left"]) + _count_total(tree["right"])


def _collect_leaves(tree: dict) -> List:
    """Collect all leaf values."""
    if tree["op"] != "eml":
        return [tree["val"]]
    return _collect_leaves(tree["left"]) + _collect_leaves(tree["right"])


def _subtree_depth(tree: dict) -> List[int]:
    """Return list of depths at which each leaf appears."""
    def _dfs(t, d):
        if t["op"] != "eml":
            return [d]
        return _dfs(t["left"], d + 1) + _dfs(t["right"], d + 1)
    return _dfs(tree, 0)


def _balance_score(tree: dict) -> float:
    """Balance: 1 - |left_size - right_size| / total."""
    if tree["op"] != "eml":
        return 1.0
    ls = _count_total(tree["left"])
    rs = _count_total(tree["right"])
    total = ls + rs
    return 1.0 - abs(ls - rs) / total if total > 0 else 1.0


def _symmetry_score(tree: dict) -> float:
    """Fraction of internal nodes whose left/right subtrees have equal depth."""
    def _nodes(t):
        if t["op"] != "eml":
            return []
        ld = _tree_depth(t["left"])
        rd = _tree_depth(t["right"])
        return [(1 if ld == rd else 0)] + _nodes(t["left"]) + _nodes(t["right"])
    scores = _nodes(tree)
    return float(np.mean(scores)) if scores else 1.0


def extract_tree_features(tree: dict) -> np.ndarray:
    """Extract 12 hand-crafted features from an EML tree dict.

    Features (all normalized to be roughly in [0, ~10]):

    0  depth          Max tree depth (leaves = 0)
    1  eml_nodes      Count of internal EML nodes
    2  total_nodes    All nodes including leaves
    3  leaf_ratio     Leaf count / total_nodes
    4  x_fraction     Fraction of leaves that are the variable x
    5  const_mean     Mean of numeric constant leaf values (0 if none)
    6  const_std      Std of numeric constant leaf values (0 if none/one)
    7  const_range    max - min of numeric constant values (0 if none)
    8  max_const      Largest absolute constant value (0 if none)
    9  balance        Tree balance score ∈ [0, 1]
    10 symmetry       Symmetry score ∈ [0, 1]
    11 depth_variance Variance of leaf depths (0 for perfectly balanced)

    Args:
        tree: EML tree dict with keys 'op', and either 'val' (leaf) or
              'left'/'right' (internal node).

    Returns:
        np.ndarray of shape (12,), dtype float64.
    """
    depth = float(_tree_depth(tree))
    eml_nodes = float(_count_eml_nodes(tree))
    total = float(_count_total(tree))
    leaves = _collect_leaves(tree)
    leaf_count = float(len(leaves))

    leaf_ratio = leaf_count / total if total > 0 else 1.0

    x_count = sum(1 for v in leaves if v == "x")
    x_fraction = x_count / leaf_count if leaf_count > 0 else 0.0

    const_vals = [float(v) for v in leaves if v != "x"]
    if const_vals:
        const_mean = float(np.mean(const_vals))
        const_std = float(np.std(const_vals)) if len(const_vals) > 1 else 0.0
        const_range = float(np.max(const_vals) - np.min(const_vals))
        max_const = float(np.max(np.abs(const_vals)))
    else:
        const_mean = 0.0
        const_std = 0.0
        const_range = 0.0
        max_const = 0.0

    balance = _balance_score(tree)
    symmetry = _symmetry_score(tree)

    leaf_depths = _subtree_depth(tree)
    depth_var = float(np.var(leaf_depths)) if len(leaf_depths) > 1 else 0.0

    return np.array([
        depth,
        eml_nodes,
        total,
        leaf_ratio,
        x_fraction,
        const_mean,
        const_std,
        const_range,
        max_const,
        balance,
        symmetry,
        depth_var,
    ], dtype=np.float64)


# ── Experience buffer ─────────────────────────────────────────────────────────

@dataclass
class ExperienceBuffer:
    """Bounded deque of (features, reward) training examples.

    Args:
        maxlen: Maximum buffer size (oldest entries evicted when full).
    """

    maxlen: int = 500
    _buf: Deque[Tuple[np.ndarray, float]] = field(default_factory=deque)

    def __post_init__(self) -> None:
        self._buf = deque(maxlen=self.maxlen)

    def add(self, features: np.ndarray, reward: float) -> None:
        """Add a (features, reward) pair."""
        reward = float(np.clip(reward, 0.0, 1.0))
        self._buf.append((features.copy(), reward))

    def __len__(self) -> int:
        return len(self._buf)

    def as_arrays(self) -> Tuple[np.ndarray, np.ndarray]:
        """Return (X, y) arrays for training."""
        X = np.stack([f for f, _ in self._buf])
        y = np.array([r for _, r in self._buf], dtype=np.float64)
        return X, y

    def to_list(self) -> List[dict]:
        """Serialize buffer for JSON persistence."""
        return [
            {"features": f.tolist(), "reward": r}
            for f, r in self._buf
        ]

    @classmethod
    def from_list(cls, data: List[dict], maxlen: int = 500) -> "ExperienceBuffer":
        """Deserialize from JSON representation."""
        buf = cls(maxlen=maxlen)
        for item in data:
            buf.add(np.array(item["features"], dtype=np.float64), item["reward"])
        return buf


# ── MLP weights (pure numpy) ──────────────────────────────────────────────────

def _relu(x: np.ndarray) -> np.ndarray:
    return np.maximum(0.0, x)


def _sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(x, -30, 30)))


def _mlp_forward(
    x: np.ndarray,
    weights: List[Tuple[np.ndarray, np.ndarray]],
) -> float:
    """Forward pass through the MLP using numpy.

    Args:
        x:       Input feature vector, shape (n_features,).
        weights: List of (W, b) pairs per layer.

    Returns:
        Scalar output in (0, 1).
    """
    h = x.copy()
    for i, (W, b) in enumerate(weights):
        h = h @ W.T + b
        if i < len(weights) - 1:
            h = _relu(h)
        else:
            h = _sigmoid(h)
    return float(h.ravel()[0])


# ── FeatureBasedEMLScorer ─────────────────────────────────────────────────────

class FeatureBasedEMLScorer:
    """Small feature-based MLP that scores EML trees by proof promise.

    Architecture: 12 → 32 → 16 → 1 (sigmoid output ∈ [0, 1]).
    ~700 parameters.  Forward pass is pure numpy (no torch dependency).
    Training uses PyTorch (imported lazily) when available.

    Online training: call ``update(tree, reward)`` after each successful proof.
    The scorer retrains every ``retrain_every`` new examples.

    When ``not is_trained()`` (buffer too small), ``score()`` returns 0.5.

    Args:
        n_features:    Number of input features (default: 12).
        hidden:        Hidden layer sizes (default: (32, 16)).
        lr:            SGD learning rate for training.
        min_samples:   Minimum buffer size before training begins.
        retrain_every: Retrain after every N new examples.

    Example::

        from monogate.neural_scorer import FeatureBasedEMLScorer
        from monogate.search.mcts import _eml, _leaf

        scorer = FeatureBasedEMLScorer()
        tree = _eml(_leaf("x"), _leaf(1.0))

        # Before training: returns 0.5 (untrained fallback)
        print(scorer.score(tree))   # 0.5

        # Simulate training from proofs
        for _ in range(15):
            scorer.update(tree, reward=0.8)

        # After training: returns a learned score
        print(scorer.is_trained())  # True
        print(scorer.score(tree))   # float in [0, 1]
    """

    def __init__(
        self,
        n_features: int = N_FEATURES,
        hidden: Tuple[int, ...] = (32, 16),
        lr: float = 0.01,
        min_samples: int = 10,
        retrain_every: int = 10,
    ) -> None:
        self.n_features = n_features
        self.hidden = hidden
        self.lr = lr
        self.min_samples = min_samples
        self.retrain_every = retrain_every

        self._buffer = ExperienceBuffer()
        self._n_since_retrain = 0
        self._trained = False

        # Initialise weights randomly (He initialisation)
        self._weights: List[Tuple[np.ndarray, np.ndarray]] = []
        self._init_weights()

    # ── Public API ────────────────────────────────────────────────────────────

    def score(self, tree: dict) -> float:
        """Score an EML tree.  Higher = more likely to lead to a short proof.

        Returns 0.5 (neutral) when the scorer has not yet been trained.

        Args:
            tree: EML tree dict.

        Returns:
            Float in [0, 1].
        """
        if not self._trained:
            return 0.5
        try:
            features = extract_tree_features(tree)
            features = self._normalize(features)
            return _mlp_forward(features, self._weights)
        except Exception:
            return 0.5

    def update(self, tree: dict, reward: float) -> None:
        """Record a proof outcome and retrain if due.

        Args:
            tree:   EML witness tree from a successful proof.
            reward: Proof quality score.  Typically ``1.0 / (1.0 + node_count)``.
        """
        try:
            features = extract_tree_features(tree)
        except Exception:
            return

        self._buffer.add(features, reward)
        self._n_since_retrain += 1

        if (len(self._buffer) >= self.min_samples
                and self._n_since_retrain >= self.retrain_every):
            self._retrain()
            self._n_since_retrain = 0

    def is_trained(self) -> bool:
        """Return True if the scorer has been trained at least once."""
        return self._trained

    def save(self, path: str) -> None:
        """Persist weights and buffer to a JSON file.

        Args:
            path: Destination file path (will be created/overwritten).
        """
        data = {
            "n_features": self.n_features,
            "hidden": list(self.hidden),
            "lr": self.lr,
            "min_samples": self.min_samples,
            "retrain_every": self.retrain_every,
            "trained": self._trained,
            "weights": [
                {"W": W.tolist(), "b": b.tolist()}
                for W, b in self._weights
            ],
            "buffer": self._buffer.to_list(),
            "norm_mean": self._norm_mean.tolist() if self._norm_mean is not None else None,
            "norm_std": self._norm_std.tolist() if self._norm_std is not None else None,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def load(self, path: str) -> None:
        """Restore weights and buffer from a JSON file.

        Args:
            path: Source file path.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.n_features = data["n_features"]
        self.hidden = tuple(data["hidden"])
        self.lr = data["lr"]
        self.min_samples = data["min_samples"]
        self.retrain_every = data["retrain_every"]
        self._trained = data["trained"]
        self._weights = [
            (np.array(layer["W"]), np.array(layer["b"]))
            for layer in data["weights"]
        ]
        self._buffer = ExperienceBuffer.from_list(data["buffer"])
        self._norm_mean = (np.array(data["norm_mean"])
                           if data["norm_mean"] is not None else None)
        self._norm_std = (np.array(data["norm_std"])
                          if data["norm_std"] is not None else None)

    # ── Private helpers ───────────────────────────────────────────────────────

    def _init_weights(self) -> None:
        """He-initialised weights for all layers."""
        rng = np.random.default_rng(42)
        layer_sizes = [self.n_features] + list(self.hidden) + [1]
        self._weights = []
        for fan_in, fan_out in zip(layer_sizes[:-1], layer_sizes[1:]):
            scale = math.sqrt(2.0 / fan_in)
            W = rng.normal(0.0, scale, (fan_out, fan_in))
            b = np.zeros(fan_out)
            self._weights.append((W, b))

        self._norm_mean: Optional[np.ndarray] = None
        self._norm_std: Optional[np.ndarray] = None

    def _normalize(self, features: np.ndarray) -> np.ndarray:
        """Z-score normalise using running statistics from the buffer."""
        if self._norm_mean is None or self._norm_std is None:
            return features
        std = np.where(self._norm_std < 1e-8, 1.0, self._norm_std)
        return (features - self._norm_mean) / std

    def _retrain(self, epochs: int = 20) -> None:
        """Retrain MLP on full buffer using SGD (via torch if available)."""
        X, y = self._buffer.as_arrays()

        # Update normalisation statistics
        self._norm_mean = X.mean(axis=0)
        self._norm_std = X.std(axis=0)
        X_norm = (X - self._norm_mean) / np.where(self._norm_std < 1e-8, 1.0, self._norm_std)

        try:
            self._retrain_torch(X_norm, y, epochs)
        except ImportError:
            self._retrain_numpy(X_norm, y, epochs)

        self._trained = True

    def _retrain_torch(self, X: np.ndarray, y: np.ndarray, epochs: int) -> None:
        """Torch-based SGD training."""
        import torch
        import torch.nn as nn
        import torch.optim as optim

        # Build torch module from current layer sizes
        layer_sizes = [self.n_features] + list(self.hidden) + [1]
        layers = []
        for i, (fan_in, fan_out) in enumerate(zip(layer_sizes[:-1], layer_sizes[1:])):
            layers.append(nn.Linear(fan_in, fan_out))
            if i < len(layer_sizes) - 2:
                layers.append(nn.ReLU())
        layers.append(nn.Sigmoid())
        model = nn.Sequential(*layers)

        # Load current weights into torch model
        linear_idx = 0
        for module in model.modules():
            if isinstance(module, nn.Linear) and linear_idx < len(self._weights):
                W, b = self._weights[linear_idx]
                module.weight.data = torch.tensor(W, dtype=torch.float32)
                module.bias.data = torch.tensor(b, dtype=torch.float32)
                linear_idx += 1

        X_t = torch.tensor(X, dtype=torch.float32)
        y_t = torch.tensor(y, dtype=torch.float32).unsqueeze(1)

        optimizer = optim.SGD(model.parameters(), lr=self.lr, momentum=0.9)
        criterion = nn.MSELoss()

        model.train()
        for _ in range(epochs):
            optimizer.zero_grad()
            pred = model(X_t)
            loss = criterion(pred, y_t)
            loss.backward()
            optimizer.step()

        # Copy trained weights back to numpy
        new_weights = []
        linear_idx = 0
        for module in model.modules():
            if isinstance(module, nn.Linear):
                W = module.weight.data.numpy().copy()
                b = module.bias.data.numpy().copy()
                new_weights.append((W, b))
                linear_idx += 1
        self._weights = new_weights

    def _retrain_numpy(self, X: np.ndarray, y: np.ndarray, epochs: int) -> None:
        """Pure numpy SGD fallback (slower but no torch dependency)."""
        # Simple 2-layer backprop (fixed to support the 12→32→16→1 architecture)
        rng = np.random.default_rng(0)
        n = len(X)

        for _ in range(epochs):
            # Mini-batch SGD (shuffle)
            idx = rng.permutation(n)
            X_shuf, y_shuf = X[idx], y[idx]

            for xi, yi in zip(X_shuf, y_shuf):
                # Forward pass with stored activations
                activations = [xi]
                h = xi.copy()
                for j, (W, b) in enumerate(self._weights):
                    z = h @ W.T + b
                    h = _sigmoid(z) if j == len(self._weights) - 1 else _relu(z)
                    activations.append(h)

                # Backward pass (MSE loss)
                delta = 2.0 * (activations[-1] - yi)  # dL/d(output)

                new_weights = []
                for j in range(len(self._weights) - 1, -1, -1):
                    W, b = self._weights[j]
                    a_prev = activations[j]
                    a_cur = activations[j + 1]

                    # Gradient of activation
                    if j == len(self._weights) - 1:
                        d_act = a_cur * (1.0 - a_cur)  # sigmoid derivative
                    else:
                        d_act = (a_cur > 0).astype(float)  # relu derivative

                    dz = delta * d_act
                    dW = np.outer(dz, a_prev)
                    db = dz

                    # Update
                    W_new = W - self.lr * dW
                    b_new = b - self.lr * db
                    new_weights.insert(0, (W_new, b_new))

                    delta = dz @ W

                self._weights = new_weights

    # ── Weight export / import ────────────────────────────────────────────────

    def get_weights(self) -> list:
        """Export weights as nested lists (JSON-serializable).

        Returns a list of ``[W, b]`` pairs (one per layer), where each W and b
        is a plain Python list.  Use :meth:`set_weights` to restore.
        """
        return [(W.tolist(), b.tolist()) for W, b in self._weights]

    def set_weights(self, weights: list) -> None:
        """Load weights from nested lists (output of :meth:`get_weights`).

        Also marks the scorer as trained so that :meth:`score` returns a
        meaningful value immediately.
        """
        self._weights = [(np.array(W), np.array(b)) for W, b in weights]
        self._trained = True
