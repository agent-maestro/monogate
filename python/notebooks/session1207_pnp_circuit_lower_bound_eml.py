import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.pnp_circuit_lower_bound_eml import analyze_pnp_circuit_lower_bound_eml
result = analyze_pnp_circuit_lower_bound_eml()
print(json.dumps(result, indent=2))
