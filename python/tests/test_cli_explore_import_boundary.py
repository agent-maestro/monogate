"""Import-boundary tests for monogate.cli.explore."""

from __future__ import annotations

import importlib

from monogate.cli import explore


def test_explore_help_parser_builds_without_optional_substrate():
    parser = explore.build_parser()
    help_text = parser.format_help()
    assert "monogate-explore" in help_text
    assert "witness" in help_text


def test_explore_analyze_reports_clear_dependency_gate(monkeypatch, capsys):
    real_import = importlib.import_module

    def fake_import(name: str, package: str | None = None):
        if name == "eml_cost":
            raise ModuleNotFoundError("No module named 'eml_cost'", name="eml_cost")
        return real_import(name, package)

    monkeypatch.setattr(importlib, "import_module", fake_import)
    rc = explore.main(["analyze", "exp(x)"])
    captured = capsys.readouterr()
    assert rc == 2
    assert "optional dependency 'eml_cost'" in captured.err
    assert "Traceback" not in captured.err


def test_explore_witness_reports_clear_nested_dependency_gate(monkeypatch, capsys):
    real_import = importlib.import_module

    def fake_import(name: str, package: str | None = None):
        if name == "monogate.witness":
            raise ModuleNotFoundError("No module named 'eml_discover'", name="eml_discover")
        return real_import(name, package)

    monkeypatch.setattr(importlib, "import_module", fake_import)
    rc = explore.main(["witness", "exp(x)"])
    captured = capsys.readouterr()
    assert rc == 2
    assert "optional dependency 'eml_discover'" in captured.err
    assert "Traceback" not in captured.err
