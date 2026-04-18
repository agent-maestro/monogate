import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.macroscopic_quantum_eml import analyze_macroscopic_quantum_eml
result = analyze_macroscopic_quantum_eml()
print(json.dumps(result, indent=2, default=str))