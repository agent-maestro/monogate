"""S66 — Lean Battlefield Survey"""
import subprocess, sys
from pathlib import Path

result = subprocess.run(
    [sys.executable, "python/experiments/lean_survey_s66.py"],
    cwd=Path(__file__).parent.parent.parent,
    capture_output=True, text=True, encoding="utf-8", errors="replace"
)
print(result.stdout)
if result.returncode != 0:
    print("STDERR:", result.stderr, file=sys.stderr)
