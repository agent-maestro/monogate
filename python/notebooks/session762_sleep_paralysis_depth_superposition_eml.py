import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.sleep_paralysis_depth_superposition_eml import analyze_sleep_paralysis_depth_superposition_eml
result = analyze_sleep_paralysis_depth_superposition_eml()
print(json.dumps(result, indent=2, default=str))
