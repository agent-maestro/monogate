"""Session 202 — Information Geometry: Fisher Metric, Natural Gradient & Exponential Families (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.information_geometry_eml import analyze_information_geometry_eml
print(json.dumps(analyze_information_geometry_eml(), indent=2, default=str))
