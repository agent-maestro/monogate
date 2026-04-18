"""Session 379 notebook"""
import json, sys
sys.path.insert(0, "python")
from monogate.frontiers.rdl_langlands_bypass_eml import analyze_rdl_langlands_bypass_eml
result = analyze_rdl_langlands_bypass_eml()
print(json.dumps(result, indent=2, default=str))
