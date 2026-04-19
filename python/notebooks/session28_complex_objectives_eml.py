"""Session 28 — complex_objectives_eml."""
import json, sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
from monogate.frontiers.complex_objectives_eml import run_session28
print(json.dumps(run_session28(), indent=2, default=str))
