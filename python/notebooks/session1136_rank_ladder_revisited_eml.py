import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.rank_ladder_revisited_eml import analyze_rank_ladder_revisited_eml
result = analyze_rank_ladder_revisited_eml()
print(json.dumps(result, indent=2))
