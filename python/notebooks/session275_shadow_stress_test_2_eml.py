import json, sys
sys.path.insert(0, 'D:/monogate/python')
from monogate.frontiers.shadow_stress_test_2_eml import analyze_shadow_stress_test_2_eml
print(json.dumps(analyze_shadow_stress_test_2_eml(), indent=2, default=str))
