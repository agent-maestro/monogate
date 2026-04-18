import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.ym_dimensional_threshold_eml import analyze_ym_dimensional_threshold_eml
result = analyze_ym_dimensional_threshold_eml()
print(json.dumps(result, indent=2))
