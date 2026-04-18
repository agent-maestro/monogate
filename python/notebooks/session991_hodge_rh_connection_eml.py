import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.hodge_rh_connection_eml import analyze_hodge_rh_connection_eml
result = analyze_hodge_rh_connection_eml()
print(json.dumps(result, indent=2, default=str))