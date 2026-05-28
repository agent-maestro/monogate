"""Tests for EML-R10F proof-assistant AST and guard model."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.eml_a12_protected_lowering_interpreter import build_interpreter
from scripts.eml_r10f_proof_assistant_ast_guard_model import (
    CLAIM_FLAGS,
    build_model,
    build_model_payload,
    validate_payload,
)


def write_minimal_r10e(tmp_path: Path) -> Path:
    payload = {
        "schemaVersion": "monogate.eml_r10e_formal_compiler_proof_skeleton.v0",
        "status": "EML_R10E_FORMAL_COMPILER_PROOF_SKELETON_PASS",
        "skeleton": {
            "openObligations": [
                {"obligationId": "compiler-wide-induction", "status": "open"},
                {"obligationId": "lowering-pass-composition", "status": "open"},
            ]
        },
        "summary": {
            "compilerCorrectnessProved": False,
            "formalCompilerProofComplete": False,
        },
    }
    path = tmp_path / "r10e.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def build_a12(tmp_path: Path):
    return build_interpreter(
        tmp_path / "a12",
        tmp_path / "packets",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )


def build_tmp(tmp_path: Path):
    r10e_path = write_minimal_r10e(tmp_path)
    a12 = build_a12(tmp_path)
    return build_model(
        r10e_path,
        Path(a12["result_path"]),
        tmp_path / "r10f",
        tmp_path / "reports",
        tmp_path / "evidence",
        tmp_path / "feeds",
    )


def test_build_model_payload_links_a12_and_r10e(tmp_path):
    r10e_path = write_minimal_r10e(tmp_path)
    a12 = build_a12(tmp_path)
    r10e = json.loads(r10e_path.read_text(encoding="utf-8"))
    a12_payload = a12["payload"]
    model = build_model_payload(r10e_path, r10e, Path(a12["result_path"]), a12_payload)
    assert model["schemaVersion"] == "monogate.eml_proof_assistant_ast_guard_model.v0"
    assert model["summary"]["astNodeCount"] >= 8
    assert model["summary"]["guardCount"] >= 4
    assert model["summary"]["loweringRuleCount"] >= 4
    assert model["summary"]["a12InterpreterLinked"] is True
    assert model["a12InterpreterSummary"]["frameCount"] >= 12


def test_r10f_inherits_open_compiler_wide_induction(tmp_path):
    payload = build_tmp(tmp_path)["payload"]
    assert "compiler-wide-induction" in payload["model"]["openCompilerObligationsFromR10E"]
    assert payload["summary"]["openCompilerObligationCount"] >= 1
    assert payload["summary"]["proofAssistantFormalizationComplete"] is False
    assert payload["summary"]["compilerCorrectnessProved"] is False
    validate_payload(payload)


def test_r10f_lowering_rules_cover_protected_targets(tmp_path):
    rules = {rule["ruleId"]: rule for rule in build_tmp(tmp_path)["model"]["loweringRules"]}
    assert rules["lower-exp-minus-one-to-expm1"]["targetAst"] == "ProtectedExpm1(x)"
    assert rules["lower-log-sum-exp-to-protected"]["targetAst"] == "ProtectedLogSumExp(xs)"
    assert rules["block-unsupported-lowering"]["targetAst"] == "BlockedReview"


def test_r10f_claim_flags_remain_false(tmp_path):
    built = build_tmp(tmp_path)
    assert all(value is False for value in CLAIM_FLAGS.values())
    assert all(value is False for value in built["payload"]["claimFlags"].values())
    assert all(value is False for value in built["model"]["claimFlags"].values())
    assert all(value is False for value in built["evidence"]["claimFlags"].values())


def test_r10f_generated_json_files_parse(tmp_path):
    built = build_tmp(tmp_path)
    for path in [built["result_path"], built["model_path"], built["evidence_path"], built["feed_path"]]:
        json.loads(Path(path).read_text(encoding="utf-8"))


def test_r10f_cli_build_strict(tmp_path):
    r10e_path = write_minimal_r10e(tmp_path)
    a12 = build_a12(tmp_path)
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_r10f_proof_assistant_ast_guard_model.py",
            "--build",
            "--r10e-path",
            str(r10e_path),
            "--a12-path",
            a12["result_path"],
            "--out-dir",
            str(tmp_path / "r10f"),
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
    assert "EML_R10F_PROOF_ASSISTANT_AST_GUARD_MODEL_OK" in proc.stdout
