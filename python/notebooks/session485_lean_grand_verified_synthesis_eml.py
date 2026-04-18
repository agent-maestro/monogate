"""Session 485 notebook"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.lean_grand_verified_synthesis_eml import analyze_lean_grand_verified_synthesis_eml
print(json.dumps(analyze_lean_grand_verified_synthesis_eml(), indent=2, default=str))
