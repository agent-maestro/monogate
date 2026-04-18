"""Session 301 — Linguistic Evolution & Phonology"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.linguistic_evolution_phonology_eml import analyze_linguistic_evolution_phonology_eml
result = analyze_linguistic_evolution_phonology_eml()
print(json.dumps(result, indent=2, default=str))
