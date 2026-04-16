"""
monogate.fused_rust — Optional Rust-accelerated EML evaluator.

Falls back to FusedEMLActivation (Python/PyTorch) if monogate_core is not
installed.  Install the Rust extension with:

    cd monogate-core
    pip install maturin
    maturin develop --release

Exports
-------
RUST_AVAILABLE : bool
    True when monogate_core is importable.

RustFusedLayer : nn.Module | None
    A drop-in replacement for FusedEMLActivation that calls the Rust kernels
    for large batches and falls back to the PyTorch path otherwise.
    None when monogate_core is not installed.

Example
-------
    from monogate.fused_rust import RustFusedLayer, RUST_AVAILABLE
    import torch

    if RUST_AVAILABLE:
        act = RustFusedLayer(depth=2, operator="EML")
        y   = act(torch.linspace(-1, 1, 10_000))
        print(y.shape)          # torch.Size([10000])
        print(act.throughput_mps(n=1_000_000))  # Rust M eval/sec
    else:
        print("Install monogate-core for Rust acceleration.")
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import torch
import torch.nn as nn
from torch import Tensor

if TYPE_CHECKING:
    import numpy as np

# ── Optional Rust import ──────────────────────────────────────────────────────

try:
    import monogate_core as _core  # type: ignore[import]

    RUST_AVAILABLE: bool = True
    _RUST_VERSION: str = getattr(_core, "__version__", "unknown")
except ImportError:
    RUST_AVAILABLE = False
    _RUST_VERSION = "not installed"
    _core = None  # type: ignore[assignment]

# ── Batch-size threshold for switching to Rust ────────────────────────────────

#: When the flattened input tensor has at least this many elements, the Rust
#: kernel is used.  Below this the PyTorch path avoids numpy roundtrip overhead.
RUST_BATCH_THRESHOLD: int = 512


# ── RustFusedLayer (only defined when monogate_core is available) ─────────────

def _make_rust_fused_layer():
    """Return the RustFusedLayer class (defined lazily to avoid import errors)."""

    class RustFusedLayer(nn.Module):
        """
        Fused EML activation backed by the Rust `monogate_core` extension.

        API-compatible with `FusedEMLActivation`.  For tensors with more than
        `RUST_BATCH_THRESHOLD` elements the forward pass is:

        1. Move tensor to CPU and convert to float64 NumPy array.
        2. Call the Rust kernel (rayon-parallel for large batches).
        3. Convert result back to a PyTorch tensor on the original device.

        For small tensors the PyTorch `FusedEMLActivation` path is used to
        avoid the numpy conversion overhead.

        Parameters
        ----------
        depth : int
            EML tree depth 1–3.
        operator : str
            ``"EML"`` (all EML nodes) or ``"BEST"`` (EXL inner, EML root).
        rust_threshold : int
            Minimum number of elements to engage the Rust path.
            Defaults to ``RUST_BATCH_THRESHOLD``.
        """

        def __init__(
            self,
            depth: int = 2,
            operator: str = "EML",
            rust_threshold: int = RUST_BATCH_THRESHOLD,
        ) -> None:
            super().__init__()

            if not 1 <= depth <= 3:
                raise ValueError(
                    f"RustFusedLayer requires depth in [1, 3], got {depth}. "
                    "depth=4 causes numerical overflow (Numerical Overflow Barrier)."
                )
            op = operator.upper()
            if op not in ("EML", "BEST"):
                raise ValueError(
                    f"RustFusedLayer supports 'EML' and 'BEST', got {operator!r}."
                )

            self.depth = depth
            self.operator = op
            self.rust_threshold = rust_threshold

            n_leaves = 1 << depth
            # Initialisation matches FusedEMLActivation: weights near zero, biases=1
            self.leaf_w = nn.Parameter(torch.randn(n_leaves) * 0.05)
            self.leaf_b = nn.Parameter(torch.ones(n_leaves))

            # Lazy import of Python fallback (avoids circular imports)
            self._py_fallback: nn.Module | None = None

        def _get_fallback(self) -> nn.Module:
            """Return (and cache) the Python FusedEMLActivation fallback."""
            if self._py_fallback is None:
                from monogate.compile.fused import FusedEMLActivation  # type: ignore[import]

                # Create a fallback with the *same* parameters
                fallback = FusedEMLActivation(depth=self.depth, operator=self.operator)
                fallback.leaf_w = self.leaf_w  # shared parameter objects
                fallback.leaf_b = self.leaf_b
                self._py_fallback = fallback
            return self._py_fallback

        def forward(self, x: Tensor) -> Tensor:
            """
            Apply the fused EML activation.

            Uses the Rust kernel for large tensors; falls back to PyTorch
            for small tensors or when running on a non-CPU device.

            Parameters
            ----------
            x : Tensor
                Any-shape tensor.

            Returns
            -------
            Tensor
                Same shape as ``x``.
            """
            import numpy as np

            shape = x.shape
            n = x.numel()

            # Use Rust path only for CPU tensors above the threshold.
            # Gradient computation goes through the Python path (Rust has no autograd).
            use_rust = (
                RUST_AVAILABLE
                and n >= self.rust_threshold
                and not x.requires_grad
                and x.device.type == "cpu"
            )

            if use_rust:
                flat_np: np.ndarray = (
                    x.detach().reshape(-1).to(torch.float64).numpy()
                )
                w_np: np.ndarray = (
                    self.leaf_w.detach().to(torch.float64).numpy()
                )
                b_np: np.ndarray = (
                    self.leaf_b.detach().to(torch.float64).numpy()
                )

                out_np: np.ndarray = _core.eval_eml_batch(
                    w_np, b_np, flat_np, depth=self.depth, operator=self.operator
                )

                out = torch.from_numpy(out_np).to(x.dtype).reshape(shape)
                return out

            # Fallback: pure PyTorch path (supports autograd, any device)
            return self._get_fallback()(x)

        def throughput_mps(self, n: int = 1_000_000, depth: int | None = None) -> float:
            """
            Measure Rust kernel throughput in millions of evaluations per second.

            Parameters
            ----------
            n : int
                Number of evaluations to time.
            depth : int, optional
                Tree depth.  Defaults to ``self.depth``.

            Returns
            -------
            float
                Throughput in M eval/sec, or 0.0 if Rust is unavailable.
            """
            if not RUST_AVAILABLE:
                return 0.0
            d = depth if depth is not None else self.depth
            return float(_core.benchmark_rust(n=n, depth=d))

        def extra_repr(self) -> str:
            n_nodes = (1 << self.depth) - 1
            rust_str = f"rust_v{_RUST_VERSION}" if RUST_AVAILABLE else "rust_unavailable"
            return (
                f"depth={self.depth}, operator={self.operator!r}, "
                f"nodes={n_nodes}, leaves={1 << self.depth}, "
                f"params={self.leaf_w.numel() * 2}, "
                f"rust_threshold={self.rust_threshold}, "
                f"backend={rust_str}"
            )

    return RustFusedLayer


if RUST_AVAILABLE:
    RustFusedLayer = _make_rust_fused_layer()
else:
    RustFusedLayer = None  # type: ignore[assignment,misc]


# ── Module-level convenience ──────────────────────────────────────────────────

def rust_info() -> None:
    """Print a summary of Rust extension availability and version."""
    if RUST_AVAILABLE:
        mps = _core.benchmark_rust(n=100_000, depth=2)
        threshold = getattr(_core, "PARALLEL_THRESHOLD", "?")
        print(f"monogate_core {_RUST_VERSION} available")
        print(f"  Quick benchmark (depth=2, n=100k): {mps:.0f} M eval/sec")
        print(f"  Rayon parallel threshold: {threshold} elements")
    else:
        print("monogate_core NOT available (Rust extension not installed)")
        print("  To install: cd monogate-core && pip install maturin && maturin develop --release")
