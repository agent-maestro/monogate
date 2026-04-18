import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.ns_godel_for_fluids_eml import analyze_ns_godel_for_fluids_eml
result = analyze_ns_godel_for_fluids_eml()
print(json.dumps(result, indent=2))
