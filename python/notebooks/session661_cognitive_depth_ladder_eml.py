import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.cognitive_depth_ladder_eml import analyze_cognitive_depth_ladder_eml
result = analyze_cognitive_depth_ladder_eml()
print(json.dumps(result, indent=2, default=str))
