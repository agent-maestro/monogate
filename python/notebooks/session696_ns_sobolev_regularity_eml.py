import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.ns_sobolev_regularity_eml import analyze_ns_sobolev_regularity_eml
result = analyze_ns_sobolev_regularity_eml()
print(json.dumps(result, indent=2, default=str))
