import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.qualia_detection_protocols_eml import analyze_qualia_detection_protocols_eml
result = analyze_qualia_detection_protocols_eml()
print(json.dumps(result, indent=2, default=str))