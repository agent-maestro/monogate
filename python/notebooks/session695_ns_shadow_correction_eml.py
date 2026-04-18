import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.ns_shadow_correction_eml import analyze_ns_shadow_correction_eml
result = analyze_ns_shadow_correction_eml()
print(json.dumps(result, indent=2, default=str))
