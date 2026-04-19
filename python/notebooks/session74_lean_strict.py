"""S74 — i-Constructibility: lean strict"""
import subprocess, sys
from pathlib import Path
result = subprocess.run(
    [sys.executable, "python/experiments/i_lean_strict_s74.py"],
    cwd=Path(__file__).parent.parent.parent,
    capture_output=True, text=True, encoding="utf-8", errors="replace"
)
print(result.stdout)
if result.returncode != 0:
    print("STDERR:", result.stderr, file=sys.stderr)
