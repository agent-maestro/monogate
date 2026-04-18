import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.millennium_tropical_barriers_eml import analyze_millennium_tropical_barriers_eml
result = analyze_millennium_tropical_barriers_eml()
print(json.dumps(result, indent=2, default=str))
