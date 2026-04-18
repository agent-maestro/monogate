import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.renormalization_eml import analyze_renormalization_eml
result = analyze_renormalization_eml()
print(json.dumps(result, indent=2, default=str))