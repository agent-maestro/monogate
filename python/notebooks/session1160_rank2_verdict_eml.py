import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.rank2_verdict_eml import analyze_rank2_verdict_eml
result = analyze_rank2_verdict_eml()
print(json.dumps(result, indent=2))
