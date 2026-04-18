"""Session 306 — Langlands Revisited"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.langlands_revisited_eml import analyze_langlands_revisited_eml
result = analyze_langlands_revisited_eml()
print(json.dumps(result, indent=2, default=str))
