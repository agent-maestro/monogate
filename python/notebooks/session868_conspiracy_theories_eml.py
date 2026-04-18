import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.conspiracy_theories_eml import analyze_conspiracy_theories_eml
result = analyze_conspiracy_theories_eml()
print(json.dumps(result, indent=2, default=str))