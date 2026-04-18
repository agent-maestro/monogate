"""Session 110 — Grand Synthesis V: The Complete EML Atlas (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.grand_synthesis_5_eml import analyze_grand_synthesis_5_eml
print(json.dumps(analyze_grand_synthesis_5_eml(), indent=2, default=str))
