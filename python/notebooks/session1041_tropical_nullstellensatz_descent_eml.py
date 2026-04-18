import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.tropical_nullstellensatz_descent_eml import analyze_tropical_nullstellensatz_descent_eml
result = analyze_tropical_nullstellensatz_descent_eml()
print(json.dumps(result, indent=2))
