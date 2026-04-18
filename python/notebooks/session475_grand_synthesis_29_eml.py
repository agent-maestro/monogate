"""Session 475 notebook"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.grand_synthesis_29_eml import analyze_grand_synthesis_29_eml
print(json.dumps(analyze_grand_synthesis_29_eml(), indent=2, default=str))
