import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.ym_functional_depth_eml import analyze_ym_functional_depth_eml
result = analyze_ym_functional_depth_eml()
print(json.dumps(result, indent=2, default=str))
