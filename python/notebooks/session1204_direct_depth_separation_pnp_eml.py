import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.direct_depth_separation_pnp_eml import analyze_direct_depth_separation_pnp_eml
result = analyze_direct_depth_separation_pnp_eml()
print(json.dumps(result, indent=2))
