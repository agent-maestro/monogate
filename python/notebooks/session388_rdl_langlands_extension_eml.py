"""Session 388 notebook"""
import json, sys
sys.path.insert(0, "python")
from monogate.frontiers.rdl_langlands_extension_eml import analyze_rdl_langlands_extension_eml
result = analyze_rdl_langlands_extension_eml()
print(json.dumps(result, indent=2, default=str))
