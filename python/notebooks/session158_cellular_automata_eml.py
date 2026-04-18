"""Session 158 — Cellular Automata (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.cellular_automata_eml import analyze_cellular_automata_eml
print(json.dumps(analyze_cellular_automata_eml(), indent=2, default=str))
