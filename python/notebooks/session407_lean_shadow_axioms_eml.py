import json, sys
sys.path.insert(0, 'python')
from monogate.frontiers.lean_shadow_axioms_eml import analyze_lean_shadow_axioms_eml
result = analyze_lean_shadow_axioms_eml()
print(json.dumps(result, indent=2, default=str))
