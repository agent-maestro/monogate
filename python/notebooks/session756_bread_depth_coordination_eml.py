import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.bread_depth_coordination_eml import analyze_bread_depth_coordination_eml
result = analyze_bread_depth_coordination_eml()
print(json.dumps(result, indent=2, default=str))
