"""Session 101 — Consciousness & Cognitive Science (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.cognition_eml import analyze_cognition_eml
print(json.dumps(analyze_cognition_eml(), indent=2, default=str))
