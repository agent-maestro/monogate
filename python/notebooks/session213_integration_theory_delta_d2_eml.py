"""Session 213 — integration theory delta d2 eml (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.integration_theory_delta_d2_eml import analyze_integration_theory_delta_d2_eml
print(json.dumps(analyze_integration_theory_delta_d2_eml(), indent=2, default=str))
