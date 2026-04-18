"""Session 302 — Extreme Materials Science"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.materials_extreme_eml import analyze_materials_extreme_eml
result = analyze_materials_extreme_eml()
print(json.dumps(result, indent=2, default=str))
