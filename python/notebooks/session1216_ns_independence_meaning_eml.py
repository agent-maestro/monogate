import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.ns_independence_meaning_eml import analyze_ns_independence_meaning_eml
result = analyze_ns_independence_meaning_eml()
print(json.dumps(result, indent=2))
