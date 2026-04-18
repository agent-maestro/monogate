import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.next_horizon_eml import analyze_next_horizon_eml
result = analyze_next_horizon_eml()
print(json.dumps(result, indent=2))
