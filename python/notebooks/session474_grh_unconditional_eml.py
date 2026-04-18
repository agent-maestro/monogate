"""Session 474 notebook"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.grh_unconditional_eml import analyze_grh_unconditional_eml
print(json.dumps(analyze_grh_unconditional_eml(), indent=2, default=str))
