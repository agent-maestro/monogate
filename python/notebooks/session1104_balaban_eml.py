import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.balaban_eml import analyze_balaban_eml
result = analyze_balaban_eml()
print(json.dumps(result, indent=2))
