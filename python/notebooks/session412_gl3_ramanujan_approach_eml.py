import json, sys
sys.path.insert(0, 'python')
from monogate.frontiers.gl3_ramanujan_approach_eml import analyze_gl3_ramanujan_approach_eml
result = analyze_gl3_ramanujan_approach_eml()
print(json.dumps(result, indent=2, default=str))
