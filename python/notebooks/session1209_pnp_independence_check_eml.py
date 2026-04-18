import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.pnp_independence_check_eml import analyze_pnp_independence_check_eml
result = analyze_pnp_independence_check_eml()
print(json.dumps(result, indent=2))
