"""Session 456 notebook"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.formal_discrete_et_eml import analyze_formal_discrete_et_eml
print(json.dumps(analyze_formal_discrete_et_eml(), indent=2, default=str))
