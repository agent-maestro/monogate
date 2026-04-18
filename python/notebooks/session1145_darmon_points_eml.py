import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.darmon_points_eml import analyze_darmon_points_eml
result = analyze_darmon_points_eml()
print(json.dumps(result, indent=2))
