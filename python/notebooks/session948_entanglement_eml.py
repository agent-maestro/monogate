import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.entanglement_eml import analyze_entanglement_eml
result = analyze_entanglement_eml()
print(json.dumps(result, indent=2, default=str))