import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.tropical_ym_eml import analyze_tropical_ym_eml
result = analyze_tropical_ym_eml()
print(json.dumps(result, indent=2))
