"""Session 340 — Developmental Biology"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.developmental_biology_eml import analyze_developmental_biology_eml
result = analyze_developmental_biology_eml()
print(json.dumps(result, indent=2, default=str))
