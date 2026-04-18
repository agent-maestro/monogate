import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.architecture_structural_eml import analyze_architecture_structural_eml
result = analyze_architecture_structural_eml()
print(json.dumps(result, indent=2, default=str))
