"""Session 323 — RH-EML Spectral Interpretations"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.rh_eml_spectral_eml import analyze_rh_eml_spectral_eml
result = analyze_rh_eml_spectral_eml()
print(json.dumps(result, indent=2, default=str))
