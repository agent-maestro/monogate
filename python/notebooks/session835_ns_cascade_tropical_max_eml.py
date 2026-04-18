import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.ns_cascade_tropical_max_eml import analyze_ns_cascade_tropical_max_eml
result = analyze_ns_cascade_tropical_max_eml()
print(json.dumps(result, indent=2, default=str))