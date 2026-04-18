import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.knitting_patterns_eml import analyze_knitting_patterns_eml
result = analyze_knitting_patterns_eml()
print(json.dumps(result, indent=2, default=str))