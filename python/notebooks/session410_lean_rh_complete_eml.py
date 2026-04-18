import json, sys
sys.path.insert(0, 'python')
from monogate.frontiers.lean_rh_complete_eml import analyze_lean_rh_complete_eml
result = analyze_lean_rh_complete_eml()
print(json.dumps(result, indent=2, default=str))
