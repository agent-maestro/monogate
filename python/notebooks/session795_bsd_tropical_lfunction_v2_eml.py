import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.bsd_tropical_lfunction_v2_eml import analyze_bsd_tropical_lfunction_v2_eml
result = analyze_bsd_tropical_lfunction_v2_eml()
print(json.dumps(result, indent=2, default=str))