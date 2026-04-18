import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.dreams_emlinf_simulation_eml import analyze_dreams_emlinf_simulation_eml
result = analyze_dreams_emlinf_simulation_eml()
print(json.dumps(result, indent=2, default=str))
