"""Tests for FEF-P32 free-target runtime-helper guard."""

from __future__ import annotations

import pytest

# Blanket-marked heavy: CLI-contract test (subprocess.run of a
# script that loads large JSON evidence). Skipped from the fast
# dev loop via `pytest -m "not heavy"`; runs in CI by default.
# A follow-up measurement pass will UN-mark individual fast files.
pytestmark = pytest.mark.heavy

import json
from pathlib import Path
import subprocess
import sys

from scripts.fef_p32_free_target_runtime_helper_guard import (
    CLAIM_FLAGS,
    build_outputs,
    build_payload,
    validate_payload,
)


def test_fef_p32_all_free_targets_emit_and_validate():
    payload = build_payload()
    validate_payload(payload)
    summary = payload["summary"]
    assert payload["status"] == "FEF_P32_FREE_TARGET_RUNTIME_HELPER_GUARD_PASS"
    assert payload["sourceFixture"] == "generated/runtime_helper_mix.eml"
    assert summary["freeTargetCount"] == 13
    assert summary["emissionPassCount"] == 13
    assert summary["validationPassCount"] == 13
    assert summary["allFreeTargetsEmissionPass"] is True
    assert summary["allFreeTargetsValidationPass"] is True


def test_fef_p32_expected_free_target_set():
    payload = build_payload()
    targets = [row["target"] for row in payload["targetRows"]]
    assert targets == [
        "c",
        "cpp",
        "rust",
        "python",
        "go",
        "java",
        "kotlin",
        "csharp",
        "javascript",
        "wasm",
        "matlab",
        "lean",
        "zkproof",
    ]


def test_fef_p32_records_validation_tiers():
    payload = build_payload()
    by_target = {row["target"]: row for row in payload["targetRows"]}
    assert by_target["c"]["validationLevel"] == "local_toolchain_syntax"
    assert by_target["cpp"]["validationLevel"] == "local_toolchain_syntax"
    assert by_target["rust"]["validationLevel"] == "local_toolchain_syntax"
    assert by_target["python"]["validationLevel"] == "local_toolchain_syntax"
    assert by_target["javascript"]["validationLevel"] == "local_toolchain_syntax"
    assert by_target["java"]["validationLevel"] == "local_toolchain_syntax"
    assert by_target["lean"]["validationLevel"] == "local_toolchain_syntax_with_sorry_allowed"
    assert by_target["zkproof"]["validationLevel"] == "json_schema_structural"
    assert by_target["wasm"]["validationLevel"] in {"wasm_llvm_ir_structural", "wasm_magic_structural"}


def test_fef_p32_keeps_broad_claims_false():
    payload = build_payload()
    summary = payload["summary"]
    assert summary["allFreeTargetsPublicReadyClaim"] is False
    assert summary["targetAllReadyClaim"] is False
    assert summary["compilerCorrectnessClaim"] is False
    assert summary["formalEquivalenceClaim"] is False
    assert summary["runtimePerformanceClaim"] is False
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in payload["claimFlags"].values())


def test_fef_p32_writes_outputs(tmp_path):
    built = build_outputs(
        tmp_path / "results",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )
    for key in ["result_path", "evidence_path", "feed_path"]:
        json.loads(Path(built[key]).read_text(encoding="utf-8"))
    assert Path(built["report_path"]).read_text(encoding="utf-8").startswith("# FEF-P32")


def test_fef_p32_cli_build_strict(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/fef_p32_free_target_runtime_helper_guard.py",
            "--build",
            "--out-dir",
            str(tmp_path / "results"),
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
    assert "FEF_P32_FREE_TARGET_RUNTIME_HELPER_GUARD_OK" in proc.stdout
