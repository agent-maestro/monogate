import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.roundabouts_vs_intersections_eml import analyze_roundabouts_vs_intersections_eml
result = analyze_roundabouts_vs_intersections_eml()
print(json.dumps(result, indent=2, default=str))