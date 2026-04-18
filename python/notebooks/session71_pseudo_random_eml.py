"""Session 71 — Pseudo vs True Randomness & EML (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.pseudo_random_eml import analyze_pseudo_random_eml

result = analyze_pseudo_random_eml()
print(json.dumps(result, indent=2, default=str))
