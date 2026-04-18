"""Session 383 notebook"""
import json, sys
sys.path.insert(0, "python")
from monogate.frontiers.rdl_self_referential_eml import analyze_rdl_self_referential_eml
result = analyze_rdl_self_referential_eml()
print(json.dumps(result, indent=2, default=str))
