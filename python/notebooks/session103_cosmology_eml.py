"""Session 103 — Cosmology & Early Universe (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.cosmology_eml import analyze_cosmology_eml
print(json.dumps(analyze_cosmology_eml(), indent=2, default=str))
