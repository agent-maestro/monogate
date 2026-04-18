import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.cross_millennium_unification_eml import analyze_cross_millennium_unification_eml
result = analyze_cross_millennium_unification_eml()
print(json.dumps(result, indent=2, default=str))
