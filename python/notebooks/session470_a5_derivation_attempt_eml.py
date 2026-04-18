"""Session 470 notebook"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.a5_derivation_attempt_eml import analyze_a5_derivation_attempt_eml
print(json.dumps(analyze_a5_derivation_attempt_eml(), indent=2, default=str))
