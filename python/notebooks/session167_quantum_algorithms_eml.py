"""Session 167 — notebook script"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.quantum_algorithms_eml import analyze_quantum_algorithms_eml
print(json.dumps(analyze_quantum_algorithms_eml(), indent=2, default=str))
