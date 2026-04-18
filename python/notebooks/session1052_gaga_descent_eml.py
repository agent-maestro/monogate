import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.gaga_descent_eml import analyze_gaga_descent_eml
result = analyze_gaga_descent_eml()
print(json.dumps(result, indent=2))
