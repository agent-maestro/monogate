import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.hodge_strongest_route_eml import analyze_hodge_strongest_route_eml
result = analyze_hodge_strongest_route_eml()
print(json.dumps(result, indent=2))
