import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.eml4_descent_obstruction_eml import analyze_eml4_descent_obstruction_eml
result = analyze_eml4_descent_obstruction_eml()
print(json.dumps(result, indent=2))
