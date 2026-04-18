import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.quantum_chaos_eml import analyze_quantum_chaos_eml
result = analyze_quantum_chaos_eml()
print(json.dumps(result, indent=2, default=str))