import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.hodge_weight_filtration_id_eml import analyze_hodge_weight_filtration_id_eml
result = analyze_hodge_weight_filtration_id_eml()
print(json.dumps(result, indent=2, default=str))
