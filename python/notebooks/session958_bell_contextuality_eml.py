import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.bell_contextuality_eml import analyze_bell_contextuality_eml
result = analyze_bell_contextuality_eml()
print(json.dumps(result, indent=2, default=str))