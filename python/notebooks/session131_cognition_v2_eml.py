"""Session 131 — Consciousness Deep II: EML Models of Attention, Insight & Qualia (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.cognition_v2_eml import analyze_cognition_v2_eml
print(json.dumps(analyze_cognition_v2_eml(), indent=2, default=str))
