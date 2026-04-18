import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.ns_double_independence_eml import analyze_ns_double_independence_eml
result = analyze_ns_double_independence_eml()
print(json.dumps(result, indent=2))
