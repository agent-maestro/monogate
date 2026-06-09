"""Private structural validator for training-cost I/O contract fixtures."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

ACCEPT_DISPOSITION = "accept_contract_shape"
REJECT_DISPOSITION = "reject_contract_shape"


@dataclass(frozen=True)
class ContractFixtureValidationResult:
    """Bounded validation result for one private I/O contract fixture."""

    disposition: str
    errors: tuple[str, ...]

    @property
    def accepted(self) -> bool:
        return self.disposition == "accept"


def validate_io_contract_fixture(fixture: dict[str, Any], contract: dict[str, Any]) -> ContractFixtureValidationResult:
    """Validate a PROD-A13 I/O contract fixture definition.

    This checks the shape of private fixture metadata only. It does not validate
    estimator semantics, estimate values, runtime behavior, calibration, or
    public readiness.
    """

    errors: list[str] = []
    expected = fixture.get("expectedDisposition")
    required_fields = set(contract.get("requiredFields", []))
    required_caveats = contract.get("requiredCaveats", [])
    required_blocked_claims = contract.get("requiredBlockedClaims", [])
    required_false_flags = set(contract.get("requiredFalseClaimFlags", []))

    if expected not in {ACCEPT_DISPOSITION, REJECT_DISPOSITION}:
        errors.append("expectedDisposition must be accept_contract_shape or reject_contract_shape")

    if expected == ACCEPT_DISPOSITION:
        _validate_accepted_fixture(fixture, errors)
    elif expected == REJECT_DISPOSITION:
        _validate_rejection_fixture(fixture, errors)

    if len(required_fields) != 8:
        errors.append("contract must require eight output fields")
    for field in ["calibration_caveats", "blocked_claims", "reviewer_next_steps"]:
        if field not in required_fields:
            errors.append(f"contract missing required output field: {field}")
    if len(required_caveats) < 5:
        errors.append("contract must require the full caveat set")
    if len(required_blocked_claims) < 8:
        errors.append("contract must require blocked claim carriage")
    for flag in ["training_savings_claim", "estimator_accuracy_claim", "runtime_performance_claim"]:
        if flag not in required_false_flags:
            errors.append(f"contract missing required false flag: {flag}")

    if expected == REJECT_DISPOSITION and not errors:
        return ContractFixtureValidationResult(disposition="reject", errors=("rejection fixture carries blocked mutation",))
    return ContractFixtureValidationResult(disposition="reject" if errors else "accept", errors=tuple(errors))


def _validate_accepted_fixture(fixture: dict[str, Any], errors: list[str]) -> None:
    if not fixture.get("inputRef"):
        errors.append("accepted fixture must name inputRef")
    output_views = fixture.get("outputViews")
    if not isinstance(output_views, list) or not output_views:
        errors.append("accepted fixture must name outputViews")
    elif not any(view in {"static_expression_cost", "graph_cost_profile", "training_budget_context"} for view in output_views):
        errors.append("accepted fixture must include at least one known cost view")
    boundary = fixture.get("requiredBoundary")
    if not isinstance(boundary, str) or not boundary:
        errors.append("accepted fixture must carry requiredBoundary")
    elif not any(marker in boundary for marker in ["not runtime", "not convergence", "not measured"]):
        errors.append("accepted fixture boundary must block runtime/training truth")
    if "mutation" in fixture:
        errors.append("accepted fixture must not carry mutation")


def _validate_rejection_fixture(fixture: dict[str, Any], errors: list[str]) -> None:
    mutation = fixture.get("mutation")
    if not isinstance(mutation, str) or not mutation:
        errors.append("rejection fixture must carry mutation")
    elif not any(
        marker in mutation
        for marker in [
            "calibration_caveats",
            "blocked_claims",
            "estimator_accuracy_claim",
            "training_savings_claim",
            "cost view",
        ]
    ):
        errors.append("rejection mutation must target caveats, blocked claims, false flags, or cost views")
    if "outputViews" in fixture:
        errors.append("rejection fixture must not be shaped as accepted output view fixture")
