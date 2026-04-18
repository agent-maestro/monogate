"""Session 304 — Atmospheric Chemistry"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.atmospheric_chemistry_eml import analyze_atmospheric_chemistry_eml
result = analyze_atmospheric_chemistry_eml()
print(json.dumps(result, indent=2, default=str))
