"""Session 477 notebook"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.lean_sorry_cross_type_cancellation_eml import analyze_lean_sorry_cross_type_cancellation_eml
print(json.dumps(analyze_lean_sorry_cross_type_cancellation_eml(), indent=2, default=str))
