"""Session 82 — Chaos vs Stochastic Processes Deep (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.chaos_stochastic_eml import analyze_chaos_stochastic_eml
print(json.dumps(analyze_chaos_stochastic_eml(), indent=2, default=str))
