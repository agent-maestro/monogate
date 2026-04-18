"""Session 205 — algebraic geometry v2 eml (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.algebraic_geometry_v2_eml import analyze_algebraic_geometry_v2_eml
print(json.dumps(analyze_algebraic_geometry_v2_eml(), indent=2, default=str))
