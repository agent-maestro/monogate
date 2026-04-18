"""Session 343 — Political Science"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.political_science_eml import analyze_political_science_eml
result = analyze_political_science_eml()
print(json.dumps(result, indent=2, default=str))
