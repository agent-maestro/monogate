"""Session 204 — Statistical Mechanics Deep II: Onsager, Transfer Matrices & Partition Functions (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.stat_mech_v2_eml import analyze_stat_mech_v2_eml
print(json.dumps(analyze_stat_mech_v2_eml(), indent=2, default=str))
