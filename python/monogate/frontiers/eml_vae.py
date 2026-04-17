"""EML Normalizing Flows Prototype — Session 32.

Implements a minimal 1D Gaussian VAE where:
- The encoder outputs EML natural parameters (η₁ < 0, η₂ ∈ ℝ) instead of μ, σ
- The KL loss is computed as Bregman divergence of the Gaussian log-partition
  (proven in Session 28 to equal KL divergence for exponential families)
- The decoder uses standard Gaussian likelihood

This demonstrates that EML is the natural coordinate system for variational
inference — the KL term has an exact closed-form as an EML expression.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Optional

import torch
import torch.nn as nn
import torch.optim as optim

from monogate.information_geometry import (
    log_partition_gaussian_1d,
    kl_divergence_gaussian,
)


# ── EML natural parameter encoder ─────────────────────────────────────────────

class EMLEncoder(nn.Module):
    """Encoder that outputs EML natural parameters (η₁ < 0, η₂ ∈ ℝ).

    Standard VAEs output (μ, log σ²). This encoder outputs (η₁, η₂) where:
        η₁ = -1 / (2σ²)  → must be strictly negative
        η₂ = μ / σ²

    The constraint η₁ < 0 is enforced by mapping a real-valued output through
    -softplus, ensuring the output is always in (-∞, 0).
    """

    def __init__(self, input_dim: int = 1, hidden_dim: int = 32, latent_dim: int = 1) -> None:
        super().__init__()
        self.shared = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Tanh(),
        )
        self.eta1_head = nn.Linear(hidden_dim, latent_dim)
        self.eta2_head = nn.Linear(hidden_dim, latent_dim)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """Return (η₁, η₂) with η₁ < 0 guaranteed."""
        h = self.shared(x)
        eta1 = -nn.functional.softplus(self.eta1_head(h)) - 1e-6  # strictly < 0
        eta2 = self.eta2_head(h)
        return eta1, eta2

    def to_mu_sigma(
        self,
        eta1: torch.Tensor,
        eta2: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """Convert natural parameters to (μ, σ²)."""
        sigma2 = -1.0 / (2.0 * eta1)
        mu = -eta2 / (2.0 * eta1)
        return mu, sigma2


class EMLDecoder(nn.Module):
    """Standard Gaussian decoder — outputs (μ, fixed σ²=1) reconstruction."""

    def __init__(self, latent_dim: int = 1, hidden_dim: int = 32, output_dim: int = 1) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(latent_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.Tanh(),
            nn.Linear(hidden_dim, output_dim),
        )

    def forward(self, z: torch.Tensor) -> torch.Tensor:
        return self.net(z)


# ── EML variational loss ───────────────────────────────────────────────────────

class EMLVariationalLoss:
    """KL divergence computed as Bregman divergence of EML log-partition.

    For Gaussian encoder q(z|x) = N(μ, σ²) with prior p(z) = N(0, 1):
    KL(q||p) = Bregman_A(η_q || η_p) where A = log_partition_gaussian_1d
             = A(η_p) - A(η_q) - (η_p - η_q) · ∇A(η_q)

    Prior natural parameters: η₁_prior = -0.5, η₂_prior = 0.0  (N(0,1))
    """

    # Prior = N(0, 1) → η₁ = -1/(2·1²) = -0.5, η₂ = 0/1² = 0
    ETA1_PRIOR: float = -0.5
    ETA2_PRIOR: float = 0.0

    def __call__(
        self,
        eta1_q: torch.Tensor,
        eta2_q: torch.Tensor,
    ) -> torch.Tensor:
        """Compute per-sample KL(q||prior) using information_geometry module."""
        batch = eta1_q.shape[0]
        kl_vals = torch.zeros(batch)
        for i in range(batch):
            e1 = eta1_q[i].item()
            e2 = eta2_q[i].item()
            kl_vals[i] = kl_divergence_gaussian(
                eta1_p=e1, eta2_p=e2,
                eta1_q=self.ETA1_PRIOR, eta2_q=self.ETA2_PRIOR,
            )
        return kl_vals.mean()


def _reparameterize(
    eta1: torch.Tensor,
    eta2: torch.Tensor,
) -> torch.Tensor:
    """Sample z ~ N(μ, σ²) via reparameterization trick, using EML params."""
    sigma2 = -1.0 / (2.0 * eta1)
    mu = -eta2 / (2.0 * eta1)
    eps = torch.randn_like(mu)
    return mu + torch.sqrt(sigma2.abs() + 1e-8) * eps


# ── Training ──────────────────────────────────────────────────────────────────

@dataclass
class EMLVAETrainResult:
    elbo_history: list[float]
    recon_history: list[float]
    kl_history: list[float]
    final_elbo: float
    final_recon: float
    final_kl: float
    n_epochs: int


def train_eml_vae(
    data: torch.Tensor,
    n_epochs: int = 500,
    hidden_dim: int = 32,
    lr: float = 1e-3,
    kl_weight: float = 1.0,
    seed: int = 42,
) -> EMLVAETrainResult:
    """Train a 1-D EML VAE on input data.

    Args:
        data: (N, 1) tensor of 1-D observations.
        n_epochs: Training epochs.
        hidden_dim: Hidden layer width.
        lr: Learning rate.
        kl_weight: Beta coefficient for KL term (β-VAE).
        seed: Random seed.

    Returns:
        EMLVAETrainResult with loss histories.
    """
    torch.manual_seed(seed)
    encoder = EMLEncoder(input_dim=1, hidden_dim=hidden_dim, latent_dim=1)
    decoder = EMLDecoder(latent_dim=1, hidden_dim=hidden_dim, output_dim=1)
    kl_loss = EMLVariationalLoss()
    optimizer = optim.Adam(list(encoder.parameters()) + list(decoder.parameters()), lr=lr)

    elbo_hist, recon_hist, kl_hist = [], [], []

    for _ in range(n_epochs):
        optimizer.zero_grad()
        eta1, eta2 = encoder(data)
        z = _reparameterize(eta1, eta2)
        x_recon = decoder(z)
        recon = nn.functional.mse_loss(x_recon, data)
        kl = kl_loss(eta1.squeeze(-1), eta2.squeeze(-1))
        loss = recon + kl_weight * kl
        loss.backward()
        optimizer.step()

        elbo_hist.append(-loss.item())
        recon_hist.append(recon.item())
        kl_hist.append(kl.item())

    return EMLVAETrainResult(
        elbo_history=elbo_hist,
        recon_history=recon_hist,
        kl_history=kl_hist,
        final_elbo=elbo_hist[-1],
        final_recon=recon_hist[-1],
        final_kl=kl_hist[-1],
        n_epochs=n_epochs,
    )


def compare_eml_vs_standard_vae(
    data: torch.Tensor,
    n_epochs: int = 200,
    seed: int = 42,
) -> dict:
    """Compare EML VAE vs standard VAE (μ/log σ² encoder) training curves.

    Returns dict with keys 'eml' and 'standard', each containing training
    curves and final metrics.
    """
    eml_result = train_eml_vae(data, n_epochs=n_epochs, seed=seed)

    # Standard VAE baseline
    torch.manual_seed(seed)
    enc_std = _StandardEncoder(input_dim=1, hidden_dim=32, latent_dim=1)
    dec_std = EMLDecoder(latent_dim=1, hidden_dim=32, output_dim=1)
    opt_std = optim.Adam(list(enc_std.parameters()) + list(dec_std.parameters()), lr=1e-3)

    std_elbo_hist, std_recon_hist, std_kl_hist = [], [], []
    for _ in range(n_epochs):
        opt_std.zero_grad()
        mu, log_var = enc_std(data)
        std = torch.exp(0.5 * log_var)
        eps = torch.randn_like(mu)
        z = mu + std * eps
        x_recon = dec_std(z)
        recon = nn.functional.mse_loss(x_recon, data)
        kl = -0.5 * torch.mean(1 + log_var - mu ** 2 - log_var.exp())
        loss = recon + kl
        loss.backward()
        opt_std.step()
        std_elbo_hist.append(-loss.item())
        std_recon_hist.append(recon.item())
        std_kl_hist.append(kl.item())

    return {
        "eml": {
            "elbo_history": eml_result.elbo_history,
            "recon_history": eml_result.recon_history,
            "kl_history": eml_result.kl_history,
            "final_elbo": eml_result.final_elbo,
            "final_recon": eml_result.final_recon,
            "final_kl": eml_result.final_kl,
        },
        "standard": {
            "elbo_history": std_elbo_hist,
            "recon_history": std_recon_hist,
            "kl_history": std_kl_hist,
            "final_elbo": std_elbo_hist[-1],
            "final_recon": std_recon_hist[-1],
            "final_kl": std_kl_hist[-1],
        },
    }


class _StandardEncoder(nn.Module):
    """Standard VAE encoder: outputs (μ, log σ²)."""

    def __init__(self, input_dim: int, hidden_dim: int, latent_dim: int) -> None:
        super().__init__()
        self.shared = nn.Sequential(
            nn.Linear(input_dim, hidden_dim), nn.Tanh(),
            nn.Linear(hidden_dim, hidden_dim), nn.Tanh(),
        )
        self.mu_head = nn.Linear(hidden_dim, latent_dim)
        self.logvar_head = nn.Linear(hidden_dim, latent_dim)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        h = self.shared(x)
        return self.mu_head(h), self.logvar_head(h)
