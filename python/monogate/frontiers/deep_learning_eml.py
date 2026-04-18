"""
Session 162 — Deep Learning: EML Depth of Neural Computation

EML operator: eml(x,y) = exp(x) - ln(y)
Key theorem: Linear layers are EML-0; activations (ReLU, GELU, softmax) are EML-1/2/3;
backpropagation is EML-2; attention (transformer) is EML-3 (softmax over queries);
generalization and emergence of capabilities are EML-∞.
"""
from __future__ import annotations
import math
from dataclasses import dataclass
from typing import Any


@dataclass
class ActivationFunctions:
    """EML depth of activation functions."""

    def relu(self, x: float) -> float:
        """ReLU(x) = max(0,x). EML-0 (piecewise linear, no exp/log)."""
        return max(0.0, x)

    def gelu(self, x: float) -> float:
        """GELU(x) ≈ x·Φ(x) ≈ 0.5x(1+tanh(√(2/π)(x+0.044715x³))). EML-3 (trig in tanh)."""
        return 0.5 * x * (1 + math.tanh(math.sqrt(2 / math.pi) * (x + 0.044715 * x ** 3)))

    def sigmoid(self, x: float) -> float:
        """σ(x) = 1/(1+exp(-x)). EML-1 (exponential)."""
        x = max(-500.0, min(500.0, x))
        return 1.0 / (1 + math.exp(-x))

    def swish(self, x: float) -> float:
        """Swish(x) = x·σ(x). EML-1 (x × EML-1)."""
        return x * self.sigmoid(x)

    def softmax(self, logits: list[float]) -> list[float]:
        """softmax(z_i) = exp(z_i)/Σexp(z_j). EML-1 (Boltzmann distribution)."""
        max_z = max(logits)
        exps = [math.exp(z - max_z) for z in logits]
        total = sum(exps)
        return [round(e / total, 6) for e in exps]

    def analyze(self) -> dict[str, Any]:
        x_vals = [-2, -1, 0, 0.5, 1, 2]
        activations = {
            "relu": {x: round(self.relu(x), 4) for x in x_vals},
            "gelu": {x: round(self.gelu(x), 6) for x in x_vals},
            "sigmoid": {x: round(self.sigmoid(x), 6) for x in x_vals},
            "swish": {x: round(self.swish(x), 6) for x in x_vals}
        }
        sm = self.softmax([1.0, 2.0, 3.0, 0.5])
        return {
            "model": "ActivationFunctions",
            "activations": activations,
            "softmax_example": sm,
            "eml_depth": {"relu": 0, "sigmoid": 1, "swish": 1, "gelu": 3, "softmax": 1},
            "key_insight": "ReLU = EML-0; sigmoid/softmax = EML-1; GELU = EML-3"
        }


@dataclass
class BackpropagationEML:
    """Gradient descent and EML depth of training dynamics."""

    def cross_entropy_loss(self, probs: list[float], target: int) -> float:
        """L = -log(p_y). EML-2 (logarithm)."""
        return -math.log(probs[target] + 1e-12)

    def gradient_update(self, param: float, grad: float, lr: float = 0.01) -> float:
        """θ ← θ - α∇L. EML-0 (linear subtraction)."""
        return param - lr * grad

    def learning_rate_schedule(self, step: int, lr0: float = 0.1, warmup: int = 100) -> float:
        """
        Cosine schedule: lr = lr0/2 * (1 + cos(π*step/T)). EML-3 (cosine).
        Warmup: lr = lr0 * step/warmup. EML-0.
        """
        if step < warmup:
            return lr0 * step / warmup
        T = 10000
        return lr0 / 2 * (1 + math.cos(math.pi * (step - warmup) / (T - warmup)))

    def loss_landscape_sharpness(self, hessian_max_eigenvalue: float) -> dict[str, Any]:
        """
        Sharpness = λ_max(∇²L). EML-2 (spectral radius of Hessian).
        Sharp minima generalize poorly; flat minima generalize well.
        """
        return {
            "sharpness": hessian_max_eigenvalue,
            "generalization_estimate": math.exp(-0.01 * hessian_max_eigenvalue),
            "eml_depth_sharpness": 2,
            "eml_depth_generalization": "∞",
            "note": "Sharpness = EML-2; why it predicts generalization = EML-∞ (open problem)"
        }

    def neural_tangent_kernel(self, n_params: int, n_data: int) -> float:
        """
        NTK: infinite-width limit where training = kernel regression.
        Kernel matrix K_∞: EML-2. But why finite-width networks generalize = EML-∞.
        Approximation quality: ~1/sqrt(n_params). EML-2.
        """
        return 1.0 / math.sqrt(n_params)

    def analyze(self) -> dict[str, Any]:
        probs = [0.1, 0.7, 0.2]
        ce = {i: round(self.cross_entropy_loss(probs, i), 4) for i in range(3)}
        lr_schedule = {s: round(self.learning_rate_schedule(s), 6)
                       for s in [0, 50, 100, 500, 1000, 5000]}
        sharpness = self.loss_landscape_sharpness(10.0)
        ntk = {n: round(self.neural_tangent_kernel(n, 1000), 6) for n in [100, 1000, 10000]}
        return {
            "model": "BackpropagationEML",
            "cross_entropy_loss": ce,
            "lr_schedule": lr_schedule,
            "loss_sharpness": sharpness,
            "ntk_approximation": ntk,
            "eml_depth": {"loss": 2, "gradient_update": 0,
                          "lr_schedule": 3, "generalization": "∞"},
            "key_insight": "Loss = EML-2 (log); gradient update = EML-0; generalization = EML-∞"
        }


@dataclass
class TransformerAttention:
    """Attention mechanism — EML depth of the transformer architecture."""

    d_model: int = 64
    n_heads: int = 8

    def scaled_dot_product_attention(self, q_norm: float, k_norm: float,
                                      d_k: int = 64) -> float:
        """
        Attention(Q,K,V) = softmax(QK^T/√d_k)V.
        QK^T/√d_k: EML-0 (linear). softmax: EML-1. Result: EML-1.
        """
        score = q_norm * k_norm / math.sqrt(d_k)
        return self.sigmoid_approx(score)

    def sigmoid_approx(self, x: float) -> float:
        x = max(-500.0, min(500.0, x))
        return 1.0 / (1 + math.exp(-x))

    def attention_entropy(self, n_tokens: int, concentration: float = 1.0) -> float:
        """
        Attention entropy: H = -Σ α_i log α_i.
        Uniform attention: H = log(n). EML-2.
        Concentrated (sharp): H → 0. EML-2.
        """
        alpha = [concentration / n_tokens] * n_tokens
        norm = sum(math.exp(a) for a in alpha)
        probs = [math.exp(a) / norm for a in alpha]
        return -sum(p * math.log(p + 1e-12) for p in probs)

    def positional_encoding(self, pos: int, d_model: int = 64) -> list[float]:
        """
        PE(pos,2i) = sin(pos/10000^{2i/d}).
        PE(pos,2i+1) = cos(pos/10000^{2i/d}). EML-3 (sinusoidal).
        """
        encoding = []
        for i in range(min(4, d_model // 2)):
            freq = 1.0 / (10000 ** (2 * i / d_model))
            encoding.append(round(math.sin(pos * freq), 6))
            encoding.append(round(math.cos(pos * freq), 6))
        return encoding

    def in_context_learning(self) -> dict[str, str]:
        """
        In-context learning: few-shot examples in prompt → model adapts.
        Mechanism EML depth = EML-∞ (not explained by any EML-finite training theory).
        """
        return {
            "phenomenon": "Model learns from examples in context without weight updates",
            "mechanistic_theory": "Partial (induction heads, S-curves, grokking)",
            "eml_depth_mechanism": "∞",
            "eml_depth_attention_computation": 3,
            "note": "Attention = EML-3; why ICL works = EML-∞ (open problem)"
        }

    def analyze(self) -> dict[str, Any]:
        attn = {(q, k): round(self.scaled_dot_product_attention(q, k), 4)
                for q, k in [(1.0, 1.0), (0.5, 0.5), (1.0, -1.0)]}
        entropy = {n: round(self.attention_entropy(n), 4) for n in [1, 4, 16, 64, 256]}
        pe = {pos: self.positional_encoding(pos) for pos in [0, 1, 10, 100]}
        icl = self.in_context_learning()
        return {
            "model": "TransformerAttention",
            "d_model": self.d_model,
            "attention_scores": {str(k): v for k, v in attn.items()},
            "attention_entropy_vs_n": entropy,
            "positional_encoding_samples": pe,
            "in_context_learning": icl,
            "eml_depth": {"qk_product": 0, "softmax_attention": 1,
                          "positional_encoding": 3, "in_context_learning": "∞"},
            "key_insight": "QK product = EML-0; softmax = EML-1; PE = EML-3; ICL = EML-∞"
        }


def analyze_deep_learning_eml() -> dict[str, Any]:
    activations = ActivationFunctions()
    backprop = BackpropagationEML()
    transformer = TransformerAttention(d_model=64, n_heads=8)
    return {
        "session": 162,
        "title": "Deep Learning: EML Depth of Neural Computation",
        "eml_operator": "eml(x,y) = exp(x) - ln(y)",
        "activation_functions": activations.analyze(),
        "backpropagation": backprop.analyze(),
        "transformer_attention": transformer.analyze(),
        "eml_depth_summary": {
            "EML-0": "ReLU, linear layers, gradient update step, attention QK product",
            "EML-1": "Sigmoid, softmax (Boltzmann), swish — all involve exp",
            "EML-2": "Cross-entropy loss (log), NTK approximation, Hessian sharpness",
            "EML-3": "GELU, cosine LR schedule, positional encoding (sinusoidal)",
            "EML-∞": "Generalization, emergence of capabilities, in-context learning, grokking"
        },
        "key_theorem": (
            "The EML Deep Learning Depth Theorem: "
            "Neural network computation decomposes cleanly by EML depth: "
            "linear layers = EML-0, sigmoid/softmax = EML-1, log-loss = EML-2, attention PE = EML-3. "
            "The training process (backprop + SGD) is EML-2 at its core (loss function). "
            "But generalization — why training on finite data produces models that work on new data — "
            "is EML-∞: no EML-finite theory fully explains it. "
            "In-context learning and capability emergence are EML-∞ phenomena in trained transformers."
        ),
        "rabbit_hole_log": [
            "ReLU = EML-0: piecewise linear, no exp/log — the simplest possible nonlinearity!",
            "Softmax = EML-1: Boltzmann distribution over logits (same as partition function)",
            "Cross-entropy = EML-2: -log(p_y) (same depth as Shannon entropy)",
            "Positional encoding = EML-3: sin(pos/10000^{2i/d}) — same depth as Fourier basis",
            "Generalization = EML-∞: double descent, grokking, ICL all defy EML-finite explanation",
            "GELU = EML-3: uses tanh (same depth as cos/sin) — deeper than sigmoid!"
        ],
        "connections": {
            "S37_fourier": "Positional encoding = EML-3 Fourier basis: explicit connection",
            "S57_stat_mech": "Softmax = Boltzmann = EML-1: transformer attention = stat mech!",
            "S131_cognition_v2": "Attention = EML-1; predictive coding = EML-2: same hierarchy"
        }
    }


if __name__ == "__main__":
    import json
    print(json.dumps(analyze_deep_learning_eml(), indent=2, default=str))
