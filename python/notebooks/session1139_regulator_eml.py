import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.regulator_eml import analyze_regulator_eml
result = analyze_regulator_eml()
print(json.dumps(result, indent=2))
