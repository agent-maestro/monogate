import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.ym_primary_route_eml import analyze_ym_primary_route_eml
result = analyze_ym_primary_route_eml()
print(json.dumps(result, indent=2))
