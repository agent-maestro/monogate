import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.light_consciousness_nde_eml import analyze_light_consciousness_nde_eml
result = analyze_light_consciousness_nde_eml()
print(json.dumps(result, indent=2, default=str))
