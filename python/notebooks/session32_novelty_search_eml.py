"""Session 32 — novelty_search_eml."""
import json, sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
from monogate.frontiers.novelty_search_eml import run_session32
print(json.dumps(run_session32(), indent=2, default=str))
