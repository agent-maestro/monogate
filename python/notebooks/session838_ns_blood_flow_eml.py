import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.ns_blood_flow_eml import analyze_ns_blood_flow_eml
result = analyze_ns_blood_flow_eml()
print(json.dumps(result, indent=2, default=str))