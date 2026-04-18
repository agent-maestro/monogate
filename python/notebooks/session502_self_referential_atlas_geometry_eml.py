"""Session 502 notebook"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.self_referential_atlas_geometry_eml import analyze_self_referential_atlas_geometry_eml
print(json.dumps(analyze_self_referential_atlas_geometry_eml(), indent=2, default=str))
