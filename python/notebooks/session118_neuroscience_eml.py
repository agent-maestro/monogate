"""Session 118 — Neuroscience & Neural Criticality: EML of the Brain (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.neuroscience_eml import analyze_neuroscience_eml
print(json.dumps(analyze_neuroscience_eml(), indent=2, default=str))
