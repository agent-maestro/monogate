"""Session 30 — sin_search_benchmark_eml."""
import json, sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
from monogate.frontiers.sin_search_benchmark_eml import run_session30
print(json.dumps(run_session30(), indent=2, default=str))
