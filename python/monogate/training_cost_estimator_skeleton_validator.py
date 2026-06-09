"""Private structural validator for non-executing estimator skeleton packets."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from monogate.training_cost_estimator_skeleton import (
    BLOCKED_CLAIMS,
    DEFAULT_CAVEATS,
    NULL_COST_VIEW_FIELDS,
    REQUIRED_FALSE_CLAIM_FLAGS,
)


@dataclass(frozen=True)
class SkeletonPacketValidationResult:
    """Bounded validation result for one private skeleton hold packet."""

    disposition: str
    errors: tuple[str, ...]

    @property
    def accepted(self) -> bool:
        return self.disposition == "accept"


def validate_skeleton_hold_packet(packet: dict[str, Any]) -> SkeletonPacketValidationResult:
    """Validate only the private non-executing skeleton hold-packet shape."""

    errors: list[str] = []
    if not isinstance(packet, dict):
        return SkeletonPacketValidationResult("reject", ("packet must be an object",))

    if packet.get("disposition") != "hold_no_estimate":
        errors.append("disposition must be hold_no_estimate")
    if not packet.get("hold_reason"):
        errors.append("hold_reason must be present")

    validation = packet.get("input_shape_validation")
    if not isinstance(validation, dict):
        errors.append("input_shape_validation must be an object")
    elif validation.get("disposition") not in {"accept_input_shape", "reject_input_shape"}:
        errors.append("input_shape_validation disposition is invalid")

    for field_name in NULL_COST_VIEW_FIELDS:
        if packet.get(field_name) is not None:
            errors.append(f"{field_name} must remain null")

    if packet.get("calibration_caveats") != list(DEFAULT_CAVEATS):
        errors.append("calibration_caveats mismatch")
    if packet.get("blocked_claims") != list(BLOCKED_CLAIMS):
        errors.append("blocked_claims mismatch")

    claim_flags = packet.get("claim_flags")
    if not isinstance(claim_flags, dict):
        errors.append("claim_flags must be an object")
    else:
        missing_flags = sorted(set(REQUIRED_FALSE_CLAIM_FLAGS) - set(claim_flags))
        if missing_flags:
            errors.append(f"missing claim flags: {missing_flags}")
        for flag in REQUIRED_FALSE_CLAIM_FLAGS:
            if claim_flags.get(flag) is not False:
                errors.append(f"{flag} must be false")

    if not isinstance(packet.get("reviewer_next_steps"), list) or not packet.get("reviewer_next_steps"):
        errors.append("reviewer_next_steps must be a non-empty list")

    return SkeletonPacketValidationResult(
        disposition="reject" if errors else "accept",
        errors=tuple(errors),
    )
