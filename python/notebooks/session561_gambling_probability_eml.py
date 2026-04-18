import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.gambling_probability_eml import analyze_gambling_probability_eml
result = analyze_gambling_probability_eml()
print(json.dumps(result, indent=2, default=str))
