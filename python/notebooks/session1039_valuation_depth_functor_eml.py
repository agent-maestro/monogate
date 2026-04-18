import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.valuation_depth_functor_eml import analyze_valuation_depth_functor_eml
result = analyze_valuation_depth_functor_eml()
print(json.dumps(result, indent=2))
