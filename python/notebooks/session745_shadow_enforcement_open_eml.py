import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.shadow_enforcement_open_eml import analyze_shadow_enforcement_open_eml
result = analyze_shadow_enforcement_open_eml()
print(json.dumps(result, indent=2, default=str))
