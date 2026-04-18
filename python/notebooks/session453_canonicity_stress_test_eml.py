"""Session 453 notebook"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.canonicity_stress_test_eml import analyze_canonicity_stress_test_eml
print(json.dumps(analyze_canonicity_stress_test_eml(), indent=2, default=str))
