import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.ns_vortex_stretching_eml3_eml import analyze_ns_vortex_stretching_eml3_eml
result = analyze_ns_vortex_stretching_eml3_eml()
print(json.dumps(result, indent=2, default=str))
