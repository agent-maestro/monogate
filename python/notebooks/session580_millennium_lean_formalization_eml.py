import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.millennium_lean_formalization_eml import analyze_millennium_lean_formalization_eml
result = analyze_millennium_lean_formalization_eml()
print(json.dumps(result, indent=2, default=str))
