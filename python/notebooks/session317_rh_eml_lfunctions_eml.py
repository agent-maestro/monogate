"""Session 317 — RH-EML L-Functions"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.rh_eml_lfunctions_eml import analyze_rh_eml_lfunctions_eml
result = analyze_rh_eml_lfunctions_eml()
print(json.dumps(result, indent=2, default=str))
