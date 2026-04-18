"""Session 303 — Behavioral Economics"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.behavioral_economics_eml import analyze_behavioral_economics_eml
result = analyze_behavioral_economics_eml()
print(json.dumps(result, indent=2, default=str))
