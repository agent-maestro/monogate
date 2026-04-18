"""Session 454 notebook"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.intrinsic_category_bridge_eml import analyze_intrinsic_category_bridge_eml
print(json.dumps(analyze_intrinsic_category_bridge_eml(), indent=2, default=str))
