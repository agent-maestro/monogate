"""Session 113 — Epidemiology & Contagion (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.epidemiology_eml import analyze_epidemiology_eml
print(json.dumps(analyze_epidemiology_eml(), indent=2, default=str))
