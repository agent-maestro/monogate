"""Session 87 — Representation Theory Higher: Kac-Moody & Moonshine (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.rep_theory_higher_eml import analyze_rep_theory_higher_eml
print(json.dumps(analyze_rep_theory_higher_eml(), indent=2, default=str))
