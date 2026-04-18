import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.sha_proved_cases_eml import analyze_sha_proved_cases_eml
result = analyze_sha_proved_cases_eml()
print(json.dumps(result, indent=2))
