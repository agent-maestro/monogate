import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.hodge_descent_bsd_rank2_eml import analyze_hodge_descent_bsd_rank2_eml
result = analyze_hodge_descent_bsd_rank2_eml()
print(json.dumps(result, indent=2))
