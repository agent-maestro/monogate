import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.instantons_eml import analyze_instantons_eml
result = analyze_instantons_eml()
print(json.dumps(result, indent=2))
