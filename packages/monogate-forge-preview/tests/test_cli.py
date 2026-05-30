from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples/gaussian.py"


def run_cli(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    env = {
        **os.environ,
        "PYTHONPATH": str(ROOT / "src"),
    }
    return subprocess.run(
        [sys.executable, "-m", "monogate_forge_preview.cli", *args],
        cwd=cwd or ROOT,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )


def test_capabilities_keeps_claims_false():
    proc = run_cli("capabilities")
    data = json.loads(proc.stdout)
    assert data["package"] == "monogate-forge-preview"
    assert data["distributionStatus"] == "local_scaffold_not_published"
    assert set(data["supportedTargets"]) == {"python", "javascript"}
    assert all(value is False for value in data["claimFlags"].values())


def test_emit_python_and_javascript(tmp_path):
    py_out = tmp_path / "gaussian.py"
    js_out = tmp_path / "gaussian.mjs"
    run_cli("emit", str(EXAMPLE), "--target", "python", "--out", str(py_out))
    run_cli("emit", str(EXAMPLE), "--target", "javascript", "--out", str(js_out))
    assert "math.exp" in py_out.read_text(encoding="utf-8")
    assert "Math.exp" in js_out.read_text(encoding="utf-8")


def test_check_executes_python_and_javascript_targets(tmp_path):
    proc = run_cli("check", str(EXAMPLE), "--targets", "python,javascript", "--work-dir", str(tmp_path))
    data = json.loads(proc.stdout)
    assert data["status"] == "pass"
    assert data["sampleCount"] == 6
    assert data["maxAbsError"] <= 1e-12


def test_packet_writes_bounded_evidence(tmp_path):
    out = tmp_path / "packet.json"
    run_cli(
        "packet",
        str(EXAMPLE),
        "--targets",
        "python,javascript",
        "--out",
        str(out),
        "--work-dir",
        str(tmp_path / "work"),
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["schemaVersion"] == "monogate.forge_preview_packet.v0"
    assert data["status"] == "pass"
    assert data["claimFlags"]["package_published"] is False
    assert data["claimFlags"]["compiler_correctness_claim"] is False


def test_blocked_target_fails(tmp_path):
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "monogate_forge_preview.cli",
            "emit",
            str(EXAMPLE),
            "--target",
            "verilog",
            "--out",
            str(tmp_path / "bad.v"),
        ],
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
        capture_output=True,
        text=True,
    )
    assert proc.returncode != 0
