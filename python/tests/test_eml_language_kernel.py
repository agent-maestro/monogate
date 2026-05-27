"""Tests for EML Language Kernel v0."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import pytest

from scripts.eml_language_kernel import (
    EmlLanguageError,
    build_fixtures,
    build_canonical_comparisons,
    canonicalize_expression,
    language_to_expression_packet,
    normalize_expression,
    parse_program,
)
from scripts.eml_packet_builder import build_result, validate_expression_packet


FIXTURES = Path("python/fixtures/eml_language_programs")


def load_fixture(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def test_normalizes_eml_and_softplus():
    normalized = normalize_expression("eml(x, softplus(y))")
    assert normalized == "exp(x) - ln(ln(1 + exp(y)))"


def test_canonical_equivalence_for_eml_expansion():
    left = canonicalize_expression("eml(x, y)")
    right = canonicalize_expression("exp(x) - ln(y)")
    assert left["canonicalHash"] == right["canonicalHash"]
    assert left["expansionTags"][0]["operator"] == "eml"


def test_canonical_equivalence_for_softplus_expansion():
    left = canonicalize_expression("softplus(x)")
    right = canonicalize_expression("ln(1 + exp(x))")
    assert left["canonicalHash"] == right["canonicalHash"]
    assert left["canonicalAst"] == right["canonicalAst"]


def test_canonicalization_sorts_commutative_add_and_mul():
    assert canonicalize_expression("x + y")["canonicalHash"] == canonicalize_expression("y + x")["canonicalHash"]
    assert canonicalize_expression("x * y")["canonicalHash"] == canonicalize_expression("y * x")["canonicalHash"]


def test_parse_softplus_pair_program():
    program = parse_program(load_fixture("softplus_pair_v0.eml"))
    assert program["schemaVersion"] == "monogate.eml_language_kernel.v0"
    assert program["program_id"] == "softplus_pair_v0"
    assert program["normalized_expression"] == "ln(exp(a) + exp(b))"
    assert program["canonicalHash"].startswith("sha256:")
    assert program["surfaceAst"]["kind"] == "op"
    assert program["expandedAst"] == program["ast"]
    assert program["guards"][0]["kind"] == "positive"
    assert program["inputs"][0]["range"] == {"min": -10.0, "max": 10.0}


def test_parse_let_guard_and_eml_primitive():
    program = parse_program(load_fixture("guarded_eml_softplus_v0.eml"))
    assert program["lets"][0]["name"] == "y_safe"
    assert program["lets"][0]["normalized_expression"] == "ln(1 + exp(y))"
    assert program["guards"][0]["expression"] == "ln(1 + exp(y))"
    assert program["normalized_expression"] == "exp(x) - ln(ln(1 + exp(y)))"
    assert [tag["operator"] for tag in program["expansionTags"]] == ["softplus", "eml"]


def test_language_program_emits_expression_packet():
    program = parse_program(load_fixture("raw_eml_primitive_v0.eml"))
    packet = language_to_expression_packet(program)
    validate_expression_packet(packet)
    assert packet["schemaVersion"] == "monogate.eml_expression_packet.v0"
    assert packet["expression"] == "exp(x) - ln(y)"
    assert packet["language_kernel"]["guards"][0]["kind"] == "positive"
    assert packet["claim_flags"]["public_savings_claim"] is False


def test_language_preserves_existing_obligation_ids():
    program = parse_program(load_fixture("softplus_pair_v0.eml"))
    packet = language_to_expression_packet(program)
    result = build_result(packet)
    obligation_ids = {card["obligationId"] for card in result["obligations"]["cards"]}
    assert "softplus_pair_v0:domain:n5:ln-argument-positive" in obligation_ids


def test_language_packet_rejects_claim_flip():
    program = parse_program(load_fixture("gaussian_energy_v0.eml"))
    packet = language_to_expression_packet(program)
    packet["claim_flags"]["public_savings_claim"] = True
    with pytest.raises(ValueError, match="public_savings_claim"):
        validate_expression_packet(packet)


def test_bad_program_rejected():
    with pytest.raises(EmlLanguageError, match="required"):
        parse_program("program missing_v0\nreturn x")


def test_build_fixtures_writes_language_and_packets(tmp_path):
    result = build_fixtures(
        FIXTURES,
        tmp_path / "language",
        tmp_path / "packets",
        tmp_path / "reports",
    )
    assert result["manifest"]["count"] >= 5
    assert len(list((tmp_path / "language").glob("*_language_2026_05_27.json"))) >= 5
    assert len(list((tmp_path / "packets").glob("*_expression_packet_2026_05_27.json"))) >= 5
    assert len(list((tmp_path / "reports").glob("*_language_kernel_2026_05_27.md"))) >= 5
    assert (tmp_path / "language" / "eml_language_canonical_comparisons_2026_05_27.json").exists()
    assert result["comparisons"]["summary"]["equivalent_count"] == 5


def test_canonical_comparison_report_has_expected_pairs():
    comparisons = build_canonical_comparisons()
    labels = {item["label"] for item in comparisons["comparisons"]}
    assert "eml primitive expansion" in labels
    assert "softplus expansion" in labels
    assert all(item["equivalentByCanonicalization"] for item in comparisons["comparisons"])


def test_cli_build_fixtures(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "python/scripts/eml_language_kernel.py",
            "--build-fixtures",
            "--out-dir",
            str(tmp_path / "language"),
            "--packet-dir",
            str(tmp_path / "packets"),
            "--report-dir",
            str(tmp_path / "reports"),
            "--strict",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "EML_LANGUAGE_KERNEL_FIXTURES_OK" in proc.stdout
    manifest_path = Path(proc.stdout.strip().split("manifest=", 1)[1])
    manifest = json.loads(manifest_path.read_text())
    assert manifest["status"] == "EML_LANGUAGE_KERNEL_FIXTURES_PASS"
