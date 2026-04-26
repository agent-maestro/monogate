"""Tests for monogate.cli.explore (folded in from eml-explore 0.1.1 in monogate 2.4.0)."""
from __future__ import annotations

import json
import os
import tempfile

import pytest

pytest.importorskip("eml_cost")
pytest.importorskip("eml_discover")
pytest.importorskip("eml_rewrite")
pytest.importorskip("eml_graph")

from monogate.cli.explore import main   # noqa: E402


def test_analyze_text_output(capsys):
    rc = main(["analyze", "exp(sin(x))"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "predicted_depth" in out
    assert "fingerprint" in out


def test_analyze_json_output(capsys):
    rc = main(["--json", "analyze", "exp(sin(x))"])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["expr"] == "exp(sin(x))"
    assert "fingerprint" in out


def test_identify_finds_registry_match(capsys):
    rc = main(["identify", "1/(1+exp(-x))"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "sigmoid" in out.lower() or "logistic" in out.lower()


def test_identify_max_caps_results(capsys):
    rc = main(["--json", "identify", "sin(x)", "--max", "2"])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert len(out["matches"]) <= 2


def test_witness_text_output(capsys):
    rc = main(["witness", "1/(1+exp(-x))"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "witness for" in out
    assert "predicted_depth" in out
    assert "Lean-verified:      yes" in out   # in EML class


def test_witness_json_output(capsys):
    rc = main(["--json", "witness", "exp(sin(x))"])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["input_expr"] == "exp(sin(x))"
    assert out["verified_in_lean"] is True


def test_witness_no_walk_skips_path(capsys):
    rc = main(["--json", "witness", "exp(x)/(1+exp(x))", "--no-walk"])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["canonical_path"] == []


def test_class_lookup_finds_members(capsys):
    rc = main(["class", "p1-d2-w1-c0"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "p1-d2-w1-c0" in out


def test_corpus_clusters_a_small_file(capsys):
    src_lines = [
        "sin(x)", "cos(y)", "exp(z)", "1 / (1 + exp(-w))", "log(t)",
    ]
    fd, path = tempfile.mkstemp(suffix=".txt", text=True)
    os.close(fd)
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(src_lines))
        rc = main(["corpus", path])
        assert rc == 0
        out = capsys.readouterr().out
        assert "cost classes" in out
    finally:
        os.unlink(path)


def test_example_cross_domain_runs(capsys):
    rc = main(["example", "cross-domain"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "Cross-domain demo" in out
    assert "perpetuity" in out


def test_example_witness_walkthrough_runs(capsys):
    rc = main(["example", "witness-walkthrough"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "textbook sigmoid" in out


def test_invalid_expression_returns_error_exit(capsys):
    rc = main(["analyze", "this is not valid sympy ((((("])
    assert rc == 2
