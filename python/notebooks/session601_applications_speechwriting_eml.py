import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.applications_speechwriting_eml import analyze_applications_speechwriting_eml
result = analyze_applications_speechwriting_eml()
print(json.dumps(result, indent=2, default=str))
