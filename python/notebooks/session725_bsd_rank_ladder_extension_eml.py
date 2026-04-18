import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.bsd_rank_ladder_extension_eml import analyze_bsd_rank_ladder_extension_eml
result = analyze_bsd_rank_ladder_extension_eml()
print(json.dumps(result, indent=2, default=str))
