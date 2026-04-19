"""Session 33 — complex_regressor_eml."""
import json, sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
from monogate.frontiers.complex_regressor_eml import run_session33
print(json.dumps(run_session33(), indent=2, default=str))
