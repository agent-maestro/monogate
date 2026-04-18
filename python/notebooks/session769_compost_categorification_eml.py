import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.compost_categorification_eml import analyze_compost_categorification_eml
result = analyze_compost_categorification_eml()
print(json.dumps(result, indent=2, default=str))
