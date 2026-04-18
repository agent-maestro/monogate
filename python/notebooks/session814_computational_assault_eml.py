import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.computational_assault_eml import analyze_computational_assault_eml
result = analyze_computational_assault_eml()
print(json.dumps(result, indent=2, default=str))