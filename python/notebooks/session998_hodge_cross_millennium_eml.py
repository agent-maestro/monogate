import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.hodge_cross_millennium_eml import analyze_hodge_cross_millennium_eml
result = analyze_hodge_cross_millennium_eml()
print(json.dumps(result, indent=2, default=str))