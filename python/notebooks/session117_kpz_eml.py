"""Session 117 — KPZ Universality & Non-Equilibrium Growth (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.kpz_eml import analyze_kpz_eml
print(json.dumps(analyze_kpz_eml(), indent=2, default=str))
