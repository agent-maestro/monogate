import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.lie_detector_eml import analyze_lie_detector_eml
result = analyze_lie_detector_eml()
print(json.dumps(result, indent=2, default=str))