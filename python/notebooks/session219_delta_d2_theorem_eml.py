"""Session 219 — delta d2 theorem eml (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.delta_d2_theorem_eml import analyze_delta_d2_theorem_eml
print(json.dumps(analyze_delta_d2_theorem_eml(), indent=2, default=str))
