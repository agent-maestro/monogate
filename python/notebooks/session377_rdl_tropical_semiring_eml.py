"""Session 377 notebook"""
import json, sys
sys.path.insert(0, "python")
from monogate.frontiers.rdl_tropical_semiring_eml import analyze_rdl_tropical_semiring_eml
result = analyze_rdl_tropical_semiring_eml()
print(json.dumps(result, indent=2, default=str))
