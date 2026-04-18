import json, sys
sys.path.insert(0, 'python')
from monogate.frontiers.lean_dirichlet_oscillation_eml import analyze_lean_dirichlet_oscillation_eml
result = analyze_lean_dirichlet_oscillation_eml()
print(json.dumps(result, indent=2, default=str))
