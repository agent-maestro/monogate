import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.l_vanishing_order_eml import analyze_l_vanishing_order_eml
result = analyze_l_vanishing_order_eml()
print(json.dumps(result, indent=2))
