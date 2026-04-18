"""Session 175 — QFT Interacting & Non-Perturbative Deep: RG Flow & Instanton Strata (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.qft_interacting_v2_eml import analyze_qft_interacting_v2_eml
print(json.dumps(analyze_qft_interacting_v2_eml(), indent=2, default=str))
