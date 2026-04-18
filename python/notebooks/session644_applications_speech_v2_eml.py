import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.applications_speech_v2_eml import analyze_applications_speech_v2_eml
result = analyze_applications_speech_v2_eml()
print(json.dumps(result, indent=2, default=str))
