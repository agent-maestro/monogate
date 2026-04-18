"""Session 452 notebook"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.gap7_eml3_zeta_zeros_eml import analyze_gap7_eml3_zeta_zeros_eml
print(json.dumps(analyze_gap7_eml3_zeta_zeros_eml(), indent=2, default=str))
