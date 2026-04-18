import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.vibrations_depth_carriers_eml import analyze_vibrations_depth_carriers_eml
result = analyze_vibrations_depth_carriers_eml()
print(json.dumps(result, indent=2, default=str))
