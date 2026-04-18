"""Session 138 — Materials Deep II: BCS Superconductivity, Mott & Topological Phases (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.materials_v2_eml import analyze_materials_v2_eml
print(json.dumps(analyze_materials_v2_eml(), indent=2, default=str))
