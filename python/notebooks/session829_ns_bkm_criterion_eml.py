import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.ns_bkm_criterion_eml import analyze_ns_bkm_criterion_eml
result = analyze_ns_bkm_criterion_eml()
print(json.dumps(result, indent=2, default=str))