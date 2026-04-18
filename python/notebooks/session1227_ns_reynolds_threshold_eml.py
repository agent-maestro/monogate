import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.ns_reynolds_threshold_eml import analyze_ns_reynolds_threshold_eml
result = analyze_ns_reynolds_threshold_eml()
print(json.dumps(result, indent=2))
