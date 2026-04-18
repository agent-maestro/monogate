import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.berkovich_gaga_eml import analyze_berkovich_gaga_eml
result = analyze_berkovich_gaga_eml()
print(json.dumps(result, indent=2))
