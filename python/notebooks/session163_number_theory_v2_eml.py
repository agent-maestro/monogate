"""Session 163 — Number Theory Deep II (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.number_theory_v2_eml import analyze_number_theory_v2_eml
print(json.dumps(analyze_number_theory_v2_eml(), indent=2, default=str))
