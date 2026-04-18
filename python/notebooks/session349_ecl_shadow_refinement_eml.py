"""Session 349 — ECL Shadow Refinement"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.ecl_shadow_refinement_eml import analyze_ecl_shadow_refinement_eml
result = analyze_ecl_shadow_refinement_eml()
print(json.dumps(result, indent=2, default=str))
