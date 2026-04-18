"""Session 447 notebook"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.gap2_intrinsic_structure_eml import analyze_gap2_intrinsic_structure_eml
print(json.dumps(analyze_gap2_intrinsic_structure_eml(), indent=2, default=str))
