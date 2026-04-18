import json, sys
sys.path.insert(0, 'D:/monogate/python')
from monogate.frontiers.consciousness_shadow_eml import analyze_consciousness_shadow_eml
print(json.dumps(analyze_consciousness_shadow_eml(), indent=2, default=str))
