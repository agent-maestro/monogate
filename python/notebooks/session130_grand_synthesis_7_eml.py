"""Session 130 — grand synthesis 7 EML (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.grand_synthesis_7_eml import analyze_grand_synthesis_7_eml
print(json.dumps(analyze_grand_synthesis_7_eml(), indent=2, default=str))
