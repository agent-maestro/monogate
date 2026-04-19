"""Session 9 — Tropical EML: Tropicalization Map & Python Simplifier."""
import json, sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
from monogate.frontiers.tropical_eml_simplifier_eml import run_session9
print(json.dumps(run_session9(), indent=2, default=str))
