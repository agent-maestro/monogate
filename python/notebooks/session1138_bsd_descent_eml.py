import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.bsd_descent_eml import analyze_bsd_descent_eml
result = analyze_bsd_descent_eml()
print(json.dumps(result, indent=2))
