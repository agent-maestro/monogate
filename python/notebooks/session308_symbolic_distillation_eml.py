"""Session 308 — Symbolic Distillation Engine"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.symbolic_distillation_eml import analyze_symbolic_distillation_eml
result = analyze_symbolic_distillation_eml()
print(json.dumps(result, indent=2, default=str))
