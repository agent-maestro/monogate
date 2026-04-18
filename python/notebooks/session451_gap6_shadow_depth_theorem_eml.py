"""Session 451 notebook"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.gap6_shadow_depth_theorem_eml import analyze_gap6_shadow_depth_theorem_eml
print(json.dumps(analyze_gap6_shadow_depth_theorem_eml(), indent=2, default=str))
