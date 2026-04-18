"""Session 450 notebook"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.gap5_axiom_system_eml import analyze_gap5_axiom_system_eml
print(json.dumps(analyze_gap5_axiom_system_eml(), indent=2, default=str))
