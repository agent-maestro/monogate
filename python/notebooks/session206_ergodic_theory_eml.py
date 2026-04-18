"""Session 206 — ergodic theory eml (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.ergodic_theory_eml import analyze_ergodic_theory_eml
print(json.dumps(analyze_ergodic_theory_eml(), indent=2, default=str))
