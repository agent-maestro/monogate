import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.scaling_laws_eml import analyze_scaling_laws_eml
result = analyze_scaling_laws_eml()
print(json.dumps(result, indent=2, default=str))