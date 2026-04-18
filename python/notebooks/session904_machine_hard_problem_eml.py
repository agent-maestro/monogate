import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.machine_hard_problem_eml import analyze_machine_hard_problem_eml
result = analyze_machine_hard_problem_eml()
print(json.dumps(result, indent=2, default=str))