"""Session 389 notebook"""
import json, sys
sys.path.insert(0, "python")
from monogate.frontiers.rdl_millennium_eml import analyze_rdl_millennium_eml
result = analyze_rdl_millennium_eml()
print(json.dumps(result, indent=2, default=str))
