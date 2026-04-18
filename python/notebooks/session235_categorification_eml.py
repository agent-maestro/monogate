import json, sys
sys.path.insert(0, 'D:/monogate/python')
from monogate.frontiers.categorification_eml import analyze_categorification_eml
result = analyze_categorification_eml()
print(json.dumps(result, indent=2, default=str))
