"""Private non-executing skeleton for the training-cost estimator lane.

This module is intentionally limited to hold packets and shape metadata. It
does not compute, infer, benchmark, calibrate, or validate estimate values.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

REQUIRED_INPUT_FIELDS = (
    "workload_id",
    "expression_ref",
    "model_family",
    "training_context",
)

NULL_COST_VIEW_FIELDS = (
    "static_expression_cost",
    "graph_cost_profile",
    "training_budget_context",
)

REQUIRED_FALSE_CLAIM_FLAGS = (
    "public_product_ready",
    "training_savings_claim",
    "estimator_accuracy_claim",
    "runtime_performance_claim",
    "broad_eml_advantage_claim",
)

BLOCKED_CLAIMS = (
    "No estimator accuracy claim is made.",
    "No training savings claim is made.",
    "No runtime performance claim is made.",
    "No model quality claim is made.",
    "No calibration claim is made.",
    "No public readiness claim is made.",
    "No SDK stability claim is made.",
    "No broad EML advantage claim is made.",
)

DEFAULT_CAVEATS = (
    "Private non-executing skeleton only.",
    "All cost-view fields remain null.",
    "Input validation is structural only.",
    "Estimator implementation remains blocked pending a later explicit gate.",
)


@dataclass(frozen=True)
class InputShapeValidation:
    """Structural input-shape result with no estimate semantics."""

    disposition: str
    missing_fields: tuple[str, ...] = ()
    present_fields: tuple[str, ...] = ()

    @property
    def accepted(self) -> bool:
        return self.disposition == "accept_input_shape"

    def to_packet(self) -> dict[str, Any]:
        return {
            "disposition": self.disposition,
            "missing_fields": list(self.missing_fields),
            "present_fields": list(self.present_fields),
        }


@dataclass(frozen=True)
class TrainingCostEstimatorSkeleton:
    """Contract-shaped shell that only emits hold/no-estimate packets."""

    artifact_id: str = "prod-a18-training-cost-estimator-non-executing-skeleton-implementation"
    disposition: str = "hold_no_estimate"
    blocked_claims: tuple[str, ...] = BLOCKED_CLAIMS
    caveats: tuple[str, ...] = DEFAULT_CAVEATS
    required_false_claim_flags: tuple[str, ...] = REQUIRED_FALSE_CLAIM_FLAGS
    null_cost_view_fields: tuple[str, ...] = NULL_COST_VIEW_FIELDS
    metadata: dict[str, Any] = field(default_factory=dict)

    def hold_packet(self, input_packet: dict[str, Any] | None = None) -> dict[str, Any]:
        return build_hold_packet(input_packet=input_packet, skeleton=self)


def validate_input_shape(input_packet: dict[str, Any]) -> InputShapeValidation:
    """Validate required input keys only; do not infer cost or runtime."""

    if not isinstance(input_packet, dict):
        return InputShapeValidation(
            disposition="reject_input_shape",
            missing_fields=REQUIRED_INPUT_FIELDS,
            present_fields=(),
        )
    present = tuple(field for field in REQUIRED_INPUT_FIELDS if field in input_packet)
    missing = tuple(field for field in REQUIRED_INPUT_FIELDS if field not in input_packet)
    return InputShapeValidation(
        disposition="accept_input_shape" if not missing else "reject_input_shape",
        missing_fields=missing,
        present_fields=present,
    )


def build_hold_packet(
    input_packet: dict[str, Any] | None = None,
    skeleton: TrainingCostEstimatorSkeleton | None = None,
) -> dict[str, Any]:
    """Return a private hold packet with all estimate views set to null."""

    active = skeleton or TrainingCostEstimatorSkeleton()
    validation = validate_input_shape(input_packet or {})
    claim_flags = {flag: False for flag in active.required_false_claim_flags}
    packet: dict[str, Any] = {
        "artifact_id": active.artifact_id,
        "disposition": active.disposition,
        "hold_reason": "estimator implementation remains blocked pending a later explicit gate",
        "input_shape_validation": validation.to_packet(),
        "calibration_caveats": list(active.caveats),
        "blocked_claims": list(active.blocked_claims),
        "claim_flags": claim_flags,
        "reviewer_next_steps": [
            "Review the non-executing skeleton before enabling any estimate-producing behavior.",
            "Approve a separate implementation gate before cost-view fields may carry values.",
        ],
    }
    for field_name in active.null_cost_view_fields:
        packet[field_name] = None
    return packet
