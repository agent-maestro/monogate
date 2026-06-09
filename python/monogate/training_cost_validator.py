"""Private structural validator for training-cost estimator fixture packets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

REQUIRED_CAVEATS = [
    "not_wall_clock_runtime",
    "not_training_savings",
    "hardware_context_missing",
    "model_quality_out_of_scope",
    "calibration_required",
]

REQUIRED_BLOCKED_CLAIMS = [
    "training cost savings",
    "estimator accuracy",
    "wall-clock runtime performance",
    "model quality improvement",
    "compiler correctness",
    "semantic preservation",
    "public product readiness",
    "hardware readiness",
    "broad EML advantage",
]

REQUIRED_FALSE_CLAIM_FLAGS = {
    "public_product_ready",
    "training_savings_claim",
    "estimator_accuracy_claim",
    "runtime_performance_claim",
    "broad_eml_advantage_claim",
}

COST_VIEW_FIELDS = ("static_expression_cost", "graph_cost_profile", "training_budget_context")


@dataclass(frozen=True)
class ValidationResult:
    """Bounded validation result for one private fixture packet."""

    disposition: str
    errors: tuple[str, ...]

    @property
    def accepted(self) -> bool:
        return self.disposition == "accept"


def validate_training_cost_fixture_packet(packet: dict[str, Any]) -> ValidationResult:
    """Validate only the private PROD-A6 fixture shape.

    This is a structural guard for internal fixture packets. It is not an
    estimator, an accuracy check, or a public schema commitment.
    """

    errors: list[str] = []

    for field in [
        "estimate_id",
        "input_summary",
        "calibration_caveats",
        "blocked_claims",
        "reviewer_next_steps",
        "claim_flags",
    ]:
        if field not in packet:
            errors.append(f"missing {field}")

    if not any(packet.get(field) is not None for field in COST_VIEW_FIELDS):
        errors.append("at least one cost view must be present")

    if packet.get("calibration_caveats") != REQUIRED_CAVEATS:
        errors.append("calibration_caveats mismatch")

    if packet.get("blocked_claims") != REQUIRED_BLOCKED_CLAIMS:
        errors.append("blocked_claims mismatch")

    claim_flags = packet.get("claim_flags")
    if not isinstance(claim_flags, dict):
        errors.append("claim_flags must be an object")
    else:
        missing_flags = sorted(REQUIRED_FALSE_CLAIM_FLAGS - set(claim_flags))
        if missing_flags:
            errors.append(f"missing claim flags: {missing_flags}")
        for flag in sorted(REQUIRED_FALSE_CLAIM_FLAGS):
            if claim_flags.get(flag) is not False:
                errors.append(f"{flag} must be false")

    if not isinstance(packet.get("input_summary"), dict):
        errors.append("input_summary must be an object")

    if not isinstance(packet.get("reviewer_next_steps"), list) or not packet.get("reviewer_next_steps"):
        errors.append("reviewer_next_steps must be a non-empty list")

    return ValidationResult(
        disposition="reject" if errors else "accept",
        errors=tuple(errors),
    )
