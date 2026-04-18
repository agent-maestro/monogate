"""Session 190 — Grand Synthesis XII: Testing the Full Framework & Horizon (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.grand_synthesis_12_eml import analyze_grand_synthesis_12_eml
print(json.dumps(analyze_grand_synthesis_12_eml(), indent=2, default=str))
