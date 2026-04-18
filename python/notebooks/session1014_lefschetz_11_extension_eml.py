import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.lefschetz_11_extension_eml import analyze_lefschetz_11_extension_eml
result = analyze_lefschetz_11_extension_eml()
print(json.dumps(result, indent=2))
