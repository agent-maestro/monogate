"""Session 97 — Statistical Mechanics Deep: Renormalization & Criticality (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.stat_mech_deep_eml import analyze_stat_mech_deep_eml
print(json.dumps(analyze_stat_mech_deep_eml(), indent=2, default=str))
