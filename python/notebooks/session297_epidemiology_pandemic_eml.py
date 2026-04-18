"""Session 297 — Epidemiology & Pandemic"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.epidemiology_pandemic_eml import analyze_epidemiology_pandemic_eml
result = analyze_epidemiology_pandemic_eml()
print(json.dumps(result, indent=2, default=str))
