"""Session 463 notebook"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.discrete_et_tropical_unification_eml import analyze_discrete_et_tropical_unification_eml
print(json.dumps(analyze_discrete_et_tropical_unification_eml(), indent=2, default=str))
