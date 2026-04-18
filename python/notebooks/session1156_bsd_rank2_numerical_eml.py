import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.bsd_rank2_numerical_eml import analyze_bsd_rank2_numerical_eml
result = analyze_bsd_rank2_numerical_eml()
print(json.dumps(result, indent=2))
