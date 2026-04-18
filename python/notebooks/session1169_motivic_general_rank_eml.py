import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.motivic_general_rank_eml import analyze_motivic_general_rank_eml
result = analyze_motivic_general_rank_eml()
print(json.dumps(result, indent=2))
