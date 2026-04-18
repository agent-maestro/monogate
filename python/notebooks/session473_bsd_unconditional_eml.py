"""Session 473 notebook"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.bsd_unconditional_eml import analyze_bsd_unconditional_eml
print(json.dumps(analyze_bsd_unconditional_eml(), indent=2, default=str))
