import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.boolean_circuits_eml import analyze_boolean_circuits_eml
result = analyze_boolean_circuits_eml()
print(json.dumps(result, indent=2))
