import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.quantum_thermodynamics_eml import analyze_quantum_thermodynamics_eml
result = analyze_quantum_thermodynamics_eml()
print(json.dumps(result, indent=2, default=str))