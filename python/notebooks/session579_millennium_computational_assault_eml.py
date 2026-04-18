import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.millennium_computational_assault_eml import analyze_millennium_computational_assault_eml
result = analyze_millennium_computational_assault_eml()
print(json.dumps(result, indent=2, default=str))
