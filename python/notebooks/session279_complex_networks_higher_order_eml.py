import json, sys
sys.path.insert(0, "python")
from monogate.frontiers.complex_networks_higher_order_eml import analyze_complex_networks_higher_order_eml
result = analyze_complex_networks_higher_order_eml()
print(json.dumps(result, indent=2, default=str))
