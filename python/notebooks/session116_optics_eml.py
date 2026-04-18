"""Session 116 — Optics, Diffraction & Quantum Coherence (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.optics_eml import analyze_optics_eml
print(json.dumps(analyze_optics_eml(), indent=2, default=str))
