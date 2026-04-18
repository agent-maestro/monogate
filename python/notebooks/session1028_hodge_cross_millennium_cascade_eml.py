import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.hodge_cross_millennium_cascade_eml import analyze_hodge_cross_millennium_cascade_eml
result = analyze_hodge_cross_millennium_cascade_eml()
print(json.dumps(result, indent=2))
