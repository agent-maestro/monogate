"""Session 94 — Biology Deep: Morphogenesis, Evolution & GRNs (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.biology_deep_eml import analyze_biology_deep_eml
print(json.dumps(analyze_biology_deep_eml(), indent=2, default=str))
