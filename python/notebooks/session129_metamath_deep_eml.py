"""Session 129 — metamath deep EML (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.metamath_deep_eml import analyze_metamath_deep_eml
print(json.dumps(analyze_metamath_deep_eml(), indent=2, default=str))
