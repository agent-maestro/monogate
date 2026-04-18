import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.ns_vortex_self_reference_eml import analyze_ns_vortex_self_reference_eml
result = analyze_ns_vortex_self_reference_eml()
print(json.dumps(result, indent=2))
