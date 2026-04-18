import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.yoneda_descent_eml import analyze_yoneda_descent_eml
result = analyze_yoneda_descent_eml()
print(json.dumps(result, indent=2))
