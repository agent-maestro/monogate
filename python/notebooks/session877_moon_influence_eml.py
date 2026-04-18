import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.moon_influence_eml import analyze_moon_influence_eml
result = analyze_moon_influence_eml()
print(json.dumps(result, indent=2, default=str))