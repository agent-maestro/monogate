"""Session 134 — Graph Theory Deep II: Spectral Methods, Percolation & Networks (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.graph_v2_eml import analyze_graph_v2_eml
print(json.dumps(analyze_graph_v2_eml(), indent=2, default=str))
