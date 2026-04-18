"""Session 220 — grand synthesis 15 eml (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.grand_synthesis_15_eml import analyze_grand_synthesis_15_eml
print(json.dumps(analyze_grand_synthesis_15_eml(), indent=2, default=str))
