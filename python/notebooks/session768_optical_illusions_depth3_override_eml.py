import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.optical_illusions_depth3_override_eml import analyze_optical_illusions_depth3_override_eml
result = analyze_optical_illusions_depth3_override_eml()
print(json.dumps(result, indent=2, default=str))
