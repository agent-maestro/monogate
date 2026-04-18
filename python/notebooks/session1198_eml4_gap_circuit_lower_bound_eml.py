import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.eml4_gap_circuit_lower_bound_eml import analyze_eml4_gap_circuit_lower_bound_eml
result = analyze_eml4_gap_circuit_lower_bound_eml()
print(json.dumps(result, indent=2))
