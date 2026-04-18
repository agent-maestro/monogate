"""Session 149 notebook script"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.foundations_v3_eml import analyze_foundations_v3_eml
print(json.dumps(analyze_foundations_v3_eml(), indent=2, default=str))
