"""Session 73 — Differential Galois Theory Deep Extensions (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.diff_galois_deep_eml import analyze_diff_galois_deep_eml

result = analyze_diff_galois_deep_eml()
print(json.dumps(result, indent=2, default=str))
