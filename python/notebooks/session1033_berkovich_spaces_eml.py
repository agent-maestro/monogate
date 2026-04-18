import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.berkovich_spaces_eml import analyze_berkovich_spaces_eml
result = analyze_berkovich_spaces_eml()
print(json.dumps(result, indent=2))
