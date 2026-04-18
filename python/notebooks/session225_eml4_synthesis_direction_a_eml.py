"""Session 225 — eml4 synthesis direction a eml (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.eml4_synthesis_direction_a_eml import analyze_eml4_synthesis_direction_a_eml
print(json.dumps(analyze_eml4_synthesis_direction_a_eml(), indent=2, default=str))
