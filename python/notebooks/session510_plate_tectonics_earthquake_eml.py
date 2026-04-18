"""Session 510 notebook"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.plate_tectonics_earthquake_eml import analyze_plate_tectonics_earthquake_eml
print(json.dumps(analyze_plate_tectonics_earthquake_eml(), indent=2, default=str))
