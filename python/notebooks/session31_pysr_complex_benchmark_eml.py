"""Session 31 — pysr_complex_benchmark_eml."""
import json, sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
from monogate.frontiers.pysr_complex_benchmark_eml import run_session31
print(json.dumps(run_session31(), indent=2, default=str))
