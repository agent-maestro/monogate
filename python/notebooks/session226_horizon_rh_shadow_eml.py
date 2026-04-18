"""Session 226 — horizon rh shadow eml (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.horizon_rh_shadow_eml import analyze_horizon_rh_shadow_eml
print(json.dumps(analyze_horizon_rh_shadow_eml(), indent=2, default=str))
