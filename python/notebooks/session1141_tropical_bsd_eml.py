import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.tropical_bsd_eml import analyze_tropical_bsd_eml
result = analyze_tropical_bsd_eml()
print(json.dumps(result, indent=2))
