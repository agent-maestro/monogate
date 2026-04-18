import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.rank2_synthesis_eml import analyze_rank2_synthesis_eml
result = analyze_rank2_synthesis_eml()
print(json.dumps(result, indent=2))
