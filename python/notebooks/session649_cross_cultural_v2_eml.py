import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.cross_cultural_v2_eml import analyze_cross_cultural_v2_eml
result = analyze_cross_cultural_v2_eml()
print(json.dumps(result, indent=2, default=str))
