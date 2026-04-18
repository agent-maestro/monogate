"""Session 104 — Graph Theory & Complex Networks (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.graph_eml import analyze_graph_eml
print(json.dumps(analyze_graph_eml(), indent=2, default=str))
