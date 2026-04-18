import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.quantum_consciousness_eml import analyze_quantum_consciousness_eml
result = analyze_quantum_consciousness_eml()
print(json.dumps(result, indent=2, default=str))