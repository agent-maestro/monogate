import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.ns_inaccessibility_eml import analyze_ns_inaccessibility_eml
result = analyze_ns_inaccessibility_eml()
print(json.dumps(result, indent=2, default=str))
