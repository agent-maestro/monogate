import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.pathological_consciousness_eml import analyze_pathological_consciousness_eml
result = analyze_pathological_consciousness_eml()
print(json.dumps(result, indent=2, default=str))
