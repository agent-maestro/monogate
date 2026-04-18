"""Session 157 — Topological Phases & Anyons (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.anyons_eml import analyze_anyons_eml
print(json.dumps(analyze_anyons_eml(), indent=2, default=str))
