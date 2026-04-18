"""Session 165 — notebook script"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.soc_eml import analyze_soc_eml
print(json.dumps(analyze_soc_eml(), indent=2, default=str))
