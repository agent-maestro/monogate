import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.toric_descent_eml import analyze_toric_descent_eml
result = analyze_toric_descent_eml()
print(json.dumps(result, indent=2))
