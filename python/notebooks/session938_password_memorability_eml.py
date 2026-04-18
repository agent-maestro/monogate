import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.password_memorability_eml import analyze_password_memorability_eml
result = analyze_password_memorability_eml()
print(json.dumps(result, indent=2, default=str))