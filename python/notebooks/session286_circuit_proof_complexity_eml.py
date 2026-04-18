import json, sys
sys.path.insert(0, "python")
from monogate.frontiers.circuit_proof_complexity_eml import analyze_circuit_proof_complexity_eml
result = analyze_circuit_proof_complexity_eml()
print(json.dumps(result, indent=2, default=str))
