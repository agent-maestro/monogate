import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.analog_photo_eml import analyze_analog_photo_eml
result = analyze_analog_photo_eml()
print(json.dumps(result, indent=2, default=str))