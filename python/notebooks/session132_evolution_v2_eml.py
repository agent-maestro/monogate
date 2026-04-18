"""Session 132 — Evolutionary Biology Deep II: Fitness Landscapes, Speciation & Punctuated Equilibrium (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.evolution_v2_eml import analyze_evolution_v2_eml
print(json.dumps(analyze_evolution_v2_eml(), indent=2, default=str))
