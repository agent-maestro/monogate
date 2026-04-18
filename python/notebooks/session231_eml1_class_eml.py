import json, sys
sys.path.insert(0, 'D:/monogate/python')
from monogate.frontiers.eml1_class_eml import analyze_eml1_class_eml
result = analyze_eml1_class_eml()
print(json.dumps(result, indent=2, default=str))
