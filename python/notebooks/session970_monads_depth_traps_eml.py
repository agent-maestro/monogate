import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.monads_depth_traps_eml import analyze_monads_depth_traps_eml
result = analyze_monads_depth_traps_eml()
print(json.dumps(result, indent=2, default=str))