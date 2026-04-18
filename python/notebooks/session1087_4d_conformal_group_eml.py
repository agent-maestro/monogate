import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.4d_conformal_group_eml import analyze_4d_conformal_group_eml
result = analyze_4d_conformal_group_eml()
print(json.dumps(result, indent=2))
