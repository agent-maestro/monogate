"""Session 404 notebook"""
import json, sys
sys.path.insert(0, "python")
from monogate.frontiers.rdl_final_synthesis_eml import analyze_rdl_final_synthesis_eml
result = analyze_rdl_final_synthesis_eml()
print(json.dumps(result, indent=2, default=str))
