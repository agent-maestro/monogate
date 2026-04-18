"""Session 446 notebook"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.gap1_canonicity_eml import analyze_gap1_canonicity_eml
print(json.dumps(analyze_gap1_canonicity_eml(), indent=2, default=str))
