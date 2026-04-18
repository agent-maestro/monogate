import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.binding_problem_type3_eml import analyze_binding_problem_type3_eml
result = analyze_binding_problem_type3_eml()
print(json.dumps(result, indent=2, default=str))
