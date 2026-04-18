"""Session 476 notebook"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.lean_sorry_deligne_1974_eml import analyze_lean_sorry_deligne_1974_eml
print(json.dumps(analyze_lean_sorry_deligne_1974_eml(), indent=2, default=str))
