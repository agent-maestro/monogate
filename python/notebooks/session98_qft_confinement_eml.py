"""Session 98 — QFT Deep: Confinement & Non-Perturbative Effects (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.qft_confinement_eml import analyze_qft_confinement_eml
print(json.dumps(analyze_qft_confinement_eml(), indent=2, default=str))
