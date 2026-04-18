"""Session 347 — ECL Langlands Bypass"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.ecl_langlands_bypass_eml import analyze_ecl_langlands_bypass_eml
result = analyze_ecl_langlands_bypass_eml()
print(json.dumps(result, indent=2, default=str))
