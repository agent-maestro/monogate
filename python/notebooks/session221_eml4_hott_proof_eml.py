"""Session 221 — eml4 hott proof eml (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.eml4_hott_proof_eml import analyze_eml4_hott_proof_eml
print(json.dumps(analyze_eml4_hott_proof_eml(), indent=2, default=str))
