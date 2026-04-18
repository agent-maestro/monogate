import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.ns_2d_not_turing_eml import analyze_ns_2d_not_turing_eml
result = analyze_ns_2d_not_turing_eml()
print(json.dumps(result, indent=2))
