import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.padic_double_zero_eml import analyze_padic_double_zero_eml
result = analyze_padic_double_zero_eml()
print(json.dumps(result, indent=2))
