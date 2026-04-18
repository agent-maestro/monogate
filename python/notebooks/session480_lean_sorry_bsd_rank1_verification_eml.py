"""Session 480 notebook"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.lean_sorry_bsd_rank1_verification_eml import analyze_lean_sorry_bsd_rank1_verification_eml
print(json.dumps(analyze_lean_sorry_bsd_rank1_verification_eml(), indent=2, default=str))
