"""Tests for EML-S27 export policy registry."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_s27_export_policy_registry import (
    CLAIM_FLAGS,
    DEFAULT_RUNTIME_FORM,
    build_outputs,
    build_payload,
    validate_payload,
    validate_policy,
)


def test_s27_builds_policy_registry_from_a14_families():
    payload, policies = build_payload()
    validate_payload(payload, policies)
    assert payload["status"] == "EML_S27_EXPORT_POLICY_REGISTRY_PASS"
    assert payload["summary"]["policyCount"] == 7
    assert payload["summary"]["coveredExportPacketCount"] == 8
    assert {policy["familyId"] for policy in policies} >= {
        "stable_sigmoid",
        "gaussian",
        "rc_decay",
        "stretched_exponential",
    }


def test_s27_stable_sigmoid_policy_carries_s24_runtime_split():
    _payload, policies = build_payload()
    stable_sigmoid = next(policy for policy in policies if policy["familyId"] == "stable_sigmoid")
    validate_policy(stable_sigmoid)
    assert stable_sigmoid["representationForm"] == "clamp_stable_sigmoid"
    assert stable_sigmoid["runtimeForm"] == "branch_stable_sigmoid"
    assert stable_sigmoid["teachingSearchForm"] == "naive_sigmoid"
    assert stable_sigmoid["cautionOrBlockedForms"] == ["naive_sigmoid"]
    assert "eml-s23-sigmoid-logistic-holdout" in stable_sigmoid["evidenceSources"]
    assert "eml-s24-sigmoid-runtime-bakeoff" in stable_sigmoid["evidenceSources"]
    assert "eml-a14-forge-efrog-export-ux" in stable_sigmoid["evidenceSources"]


def test_s27_softplus_policy_carries_s28_runtime_split():
    _payload, policies = build_payload()
    softplus = next(policy for policy in policies if policy["familyId"] == "numpy_softplus")
    validate_policy(softplus)
    assert softplus["representationForm"] == "softplus_logsumexp"
    assert softplus["runtimeForm"] == "logaddexp_softplus"
    assert softplus["teachingSearchForm"] == "naive_softplus"
    assert "naive_softplus" in softplus["cautionOrBlockedForms"]
    assert "clamp60_softplus_caution" in softplus["cautionOrBlockedForms"]
    assert "eml-s28-softplus-runtime-bakeoff" in softplus["evidenceSources"]


def test_s27_gaussian_policy_carries_s30_runtime_split():
    _payload, policies = build_payload()
    gaussian = next(policy for policy in policies if policy["familyId"] == "gaussian")
    validate_policy(gaussian)
    assert gaussian["representationForm"] == "eml_exponential_quadratic_envelope"
    assert gaussian["runtimeForm"] == "log_domain_pdf"
    assert gaussian["teachingSearchForm"] == "eml_exponential_quadratic_envelope"
    assert "clamp_exponent_caution" in gaussian["cautionOrBlockedForms"]
    assert "eml-s30-gaussian-log-normal-runtime-bakeoff" in gaussian["evidenceSources"]


def test_s27_clamp_guard_policy_carries_s31_guard_drilldown():
    _payload, policies = build_payload()
    clamp_guard = next(policy for policy in policies if policy["familyId"] == "clamp_guard")
    validate_policy(clamp_guard)
    assert clamp_guard["policyStatus"] == "guard_policy_drilldown_attached"
    assert clamp_guard["representationForm"] == "guard_owned_branch_boundary_surface"
    assert clamp_guard["runtimeForm"] == "guard_owned_branch_boundary_surface"
    assert clamp_guard["runtimeRole"] == "guard_policy_boundary_not_generic_runtime_lowering"
    assert clamp_guard["teachingSearchForm"] == "semantic_clamp_baseline"
    assert "runtime_clamp_caution" in clamp_guard["cautionOrBlockedForms"]
    assert "eml-s31-guard-owned-clamp-policy-bakeoff" in clamp_guard["evidenceSources"]


def test_s27_remaining_core_families_remain_default_until_benchmarked():
    _payload, policies = build_payload()
    by_family = {policy["familyId"]: policy for policy in policies}
    for family_id in ["rc_decay", "stretched_exponential"]:
        policy = by_family[family_id]
        assert policy["runtimeForm"] == DEFAULT_RUNTIME_FORM
        assert policy["policyStatus"] == "default_until_family_runtime_bakeoff"
        assert "no family-specific runtime bakeoff attached" in policy["unresolvedGaps"]


def test_s27_summary_preserves_claim_boundaries():
    payload, policies = build_payload()
    summary = payload["summary"]
    assert summary["runtimeAdvisoryAttachedPolicyCount"] == 3
    assert summary["defaultUntilBenchmarkedPolicyCount"] == 3
    assert summary["stableSigmoidPolicyAttached"] is True
    assert summary["softplusPolicyAttached"] is True
    assert summary["gaussianPolicyAttached"] is True
    assert summary["guardOwnedClampPolicyAttached"] is True
    assert summary["forgeBehaviorChanged"] is False
    assert summary["efrogBehaviorChanged"] is False
    assert summary["generatedTargetCodeChanged"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert summary["publicReady"] is False
    for policy in policies:
        assert policy["claimBoundary"] == "private_export_policy_metadata_only_no_compiler_behavior_change_or_runtime_performance_claim"


def test_s27_claim_flags_all_false():
    assert all(value is False for value in CLAIM_FLAGS.values())
    payload, policies = build_payload()
    assert all(value is False for value in payload["claimFlags"].values())
    for policy in policies:
        assert all(value is False for value in policy["claimFlags"].values())


def test_s27_writes_outputs_and_policy_packets(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    packet_paths = sorted((tmp_path / "packets").glob("*.json"))
    assert len(packet_paths) == 7
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# EML-S27")


def test_s27_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_s27_export_policy_registry.py",
            "--build",
            "--out-dir",
            str(tmp_path / "results"),
            "--packet-dir",
            str(tmp_path / "packets"),
            "--report-dir",
            str(tmp_path / "reports"),
            "--evidence-dir",
            str(tmp_path / "evidence"),
            "--command-feed-dir",
            str(tmp_path / "feeds"),
            "--strict",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "EML_S27_EXPORT_POLICY_REGISTRY_OK" in proc.stdout
