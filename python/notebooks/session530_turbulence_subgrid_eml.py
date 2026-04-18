import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.turbulence_subgrid_eml import analyze_turbulence_subgrid_eml
result = analyze_turbulence_subgrid_eml()
print(json.dumps(result, indent=2, default=str))
