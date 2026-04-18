import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.three_constraint_rank2_eml import analyze_three_constraint_rank2_eml
result = analyze_three_constraint_rank2_eml()
print(json.dumps(result, indent=2))
