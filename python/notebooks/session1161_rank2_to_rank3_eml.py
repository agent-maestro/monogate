import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.rank2_to_rank3_eml import analyze_rank2_to_rank3_eml
result = analyze_rank2_to_rank3_eml()
print(json.dumps(result, indent=2))
