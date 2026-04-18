import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.bsd_counterexample_hunt_eml import analyze_bsd_counterexample_hunt_eml
result = analyze_bsd_counterexample_hunt_eml()
print(json.dumps(result, indent=2))
