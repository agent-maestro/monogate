"""Session 487 notebook"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.consciousness_iit_revisited_eml import analyze_consciousness_iit_revisited_eml
print(json.dumps(analyze_consciousness_iit_revisited_eml(), indent=2, default=str))
