"""Session 152 — Chaos & Control Theory Deep II (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.chaos_control_v2_eml import analyze_chaos_control_v2_eml
print(json.dumps(analyze_chaos_control_v2_eml(), indent=2, default=str))
