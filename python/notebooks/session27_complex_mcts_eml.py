"""Session 27 — complex_mcts_eml."""
import json, sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
from monogate.frontiers.complex_mcts_eml import run_session27
print(json.dumps(run_session27(), indent=2, default=str))
