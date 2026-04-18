import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.pnp_ns_connection_eml import analyze_pnp_ns_connection_eml
result = analyze_pnp_ns_connection_eml()
print(json.dumps(result, indent=2))
