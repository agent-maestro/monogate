import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.light_dual_shadow_eml import analyze_light_dual_shadow_eml
result = analyze_light_dual_shadow_eml()
print(json.dumps(result, indent=2, default=str))
