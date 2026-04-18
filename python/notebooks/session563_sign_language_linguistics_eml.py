import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.sign_language_linguistics_eml import analyze_sign_language_linguistics_eml
result = analyze_sign_language_linguistics_eml()
print(json.dumps(result, indent=2, default=str))
