import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.ym_three_constraint_eml import analyze_ym_three_constraint_eml
result = analyze_ym_three_constraint_eml()
print(json.dumps(result, indent=2))
