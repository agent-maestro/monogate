"""Session 207 — quantum information eml (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.quantum_information_eml import analyze_quantum_information_eml
print(json.dumps(analyze_quantum_information_eml(), indent=2, default=str))
