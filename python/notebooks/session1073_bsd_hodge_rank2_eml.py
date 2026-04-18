import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.bsd_hodge_rank2_eml import analyze_bsd_hodge_rank2_eml
result = analyze_bsd_hodge_rank2_eml()
print(json.dumps(result, indent=2))
