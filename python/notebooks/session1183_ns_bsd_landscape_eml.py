import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.ns_bsd_landscape_eml import analyze_ns_bsd_landscape_eml
result = analyze_ns_bsd_landscape_eml()
print(json.dumps(result, indent=2))
