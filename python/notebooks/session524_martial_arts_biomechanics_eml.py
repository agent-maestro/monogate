"""Session 524 notebook"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.martial_arts_biomechanics_eml import analyze_martial_arts_biomechanics_eml
print(json.dumps(analyze_martial_arts_biomechanics_eml(), indent=2, default=str))
