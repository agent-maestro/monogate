import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.quantum_error_correction_eml import analyze_quantum_error_correction_eml
result = analyze_quantum_error_correction_eml()
print(json.dumps(result, indent=2, default=str))