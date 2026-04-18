"""Session 339 — Urban Systems"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.urban_systems_eml import analyze_urban_systems_eml
result = analyze_urban_systems_eml()
print(json.dumps(result, indent=2, default=str))
