import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.pnp_formal_bridge_eml import analyze_pnp_formal_bridge_eml
result = analyze_pnp_formal_bridge_eml()
print(json.dumps(result, indent=2))
