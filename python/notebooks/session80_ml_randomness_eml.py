"""Session 80 — Algorithmic Randomness Deep (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.ml_randomness_eml import analyze_ml_randomness_eml
print(json.dumps(analyze_ml_randomness_eml(), indent=2, default=str))
