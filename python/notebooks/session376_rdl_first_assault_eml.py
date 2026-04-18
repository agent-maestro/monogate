"""Session 376 notebook"""
import json, sys
sys.path.insert(0, "python")
from monogate.frontiers.rdl_first_assault_eml import analyze_rdl_first_assault_eml
result = analyze_rdl_first_assault_eml()
print(json.dumps(result, indent=2, default=str))
