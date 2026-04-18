import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.berkovich_artin_anatomy_eml import analyze_berkovich_artin_anatomy_eml
result = analyze_berkovich_artin_anatomy_eml()
print(json.dumps(result, indent=2))
