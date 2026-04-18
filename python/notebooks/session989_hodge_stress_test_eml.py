import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.hodge_stress_test_eml import analyze_hodge_stress_test_eml
result = analyze_hodge_stress_test_eml()
print(json.dumps(result, indent=2, default=str))