"""Session 519 notebook"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.origami_computational_geometry_eml import analyze_origami_computational_geometry_eml
print(json.dumps(analyze_origami_computational_geometry_eml(), indent=2, default=str))
