import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.tropical_no_inverse_computation_eml import analyze_tropical_no_inverse_computation_eml
result = analyze_tropical_no_inverse_computation_eml()
print(json.dumps(result, indent=2))
