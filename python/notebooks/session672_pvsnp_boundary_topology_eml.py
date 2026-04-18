import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.pvsnp_boundary_topology_eml import analyze_pvsnp_boundary_topology_eml
result = analyze_pvsnp_boundary_topology_eml()
print(json.dumps(result, indent=2, default=str))
