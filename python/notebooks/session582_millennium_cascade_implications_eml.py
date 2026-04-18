import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.millennium_cascade_implications_eml import analyze_millennium_cascade_implications_eml
result = analyze_millennium_cascade_implications_eml()
print(json.dumps(result, indent=2, default=str))
