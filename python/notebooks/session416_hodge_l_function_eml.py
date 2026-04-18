import json, sys
sys.path.insert(0, 'python')
from monogate.frontiers.hodge_l_function_eml import analyze_hodge_l_function_eml
result = analyze_hodge_l_function_eml()
print(json.dumps(result, indent=2, default=str))
