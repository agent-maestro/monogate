import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.seiberg_witten_eml import analyze_seiberg_witten_eml
result = analyze_seiberg_witten_eml()
print(json.dumps(result, indent=2))
