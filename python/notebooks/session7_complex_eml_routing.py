"""Session 7 — Complex EML: Single-Node Identity Enumeration & Complex BEST Routing."""
import json, sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
from monogate.frontiers.complex_eml_routing_eml import run_session7
print(json.dumps(run_session7(), indent=2, default=str))
