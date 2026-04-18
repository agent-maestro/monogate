import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.silence_structured_absence_eml import analyze_silence_structured_absence_eml
result = analyze_silence_structured_absence_eml()
print(json.dumps(result, indent=2, default=str))
