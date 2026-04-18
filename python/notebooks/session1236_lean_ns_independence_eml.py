import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.lean_ns_independence_eml import analyze_lean_ns_independence_eml
result = analyze_lean_ns_independence_eml()
print(json.dumps(result, indent=2))
