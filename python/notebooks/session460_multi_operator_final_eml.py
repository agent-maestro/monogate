"""Session 460 notebook"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.multi_operator_final_eml import analyze_multi_operator_final_eml
print(json.dumps(analyze_multi_operator_final_eml(), indent=2, default=str))
