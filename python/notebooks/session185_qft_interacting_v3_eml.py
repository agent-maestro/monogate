"""Session 185 — QFT Interacting Deep II: Confinement, RG Flow & S-Duality (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.qft_interacting_v3_eml import analyze_qft_interacting_v3_eml
print(json.dumps(analyze_qft_interacting_v3_eml(), indent=2, default=str))
