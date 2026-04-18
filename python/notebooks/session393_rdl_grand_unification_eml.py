"""Session 393 notebook"""
import json, sys
sys.path.insert(0, "python")
from monogate.frontiers.rdl_grand_unification_eml import analyze_rdl_grand_unification_eml
result = analyze_rdl_grand_unification_eml()
print(json.dumps(result, indent=2, default=str))
