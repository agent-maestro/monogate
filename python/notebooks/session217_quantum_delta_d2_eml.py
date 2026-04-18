"""Session 217 — quantum delta d2 eml (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.quantum_delta_d2_eml import analyze_quantum_delta_d2_eml
print(json.dumps(analyze_quantum_delta_d2_eml(), indent=2, default=str))
