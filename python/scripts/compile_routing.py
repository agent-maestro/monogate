#!/usr/bin/env python3
"""
Compile the private routing table into a distributable binary.

    python scripts/compile_routing.py

Reads:  monogate/_routing_private.py  (not in public repo)
Writes: monogate/_routing.pkl          (binary, not in public repo)

The binary is included in PyPI wheels via pyproject.toml package-data so that
the installed package loads the full optimized dispatch table at import time.
Run this script after any change to _routing_private.py, then rebuild the wheel.
"""

from __future__ import annotations

import pickle
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    from monogate._routing_private import ROUTING_TABLE
except ImportError:
    sys.exit(
        "ERROR: monogate/_routing_private.py not found.\n"
        "This file is private and not tracked in the public repo.\n"
        "Obtain it from the private distribution before compiling."
    )

if not isinstance(ROUTING_TABLE, dict) or not ROUTING_TABLE:
    sys.exit("ERROR: ROUTING_TABLE in _routing_private.py is empty or malformed.")

out_path = ROOT / "monogate" / "_routing.pkl"
with out_path.open("wb") as fh:
    pickle.dump(ROUTING_TABLE, fh, protocol=pickle.HIGHEST_PROTOCOL)

size = out_path.stat().st_size
print(f"Written: {out_path}  ({size} bytes, {len(ROUTING_TABLE)} ops)")
for op, name in sorted(ROUTING_TABLE.items()):
    print(f"  {op:<8} -> {name}")
