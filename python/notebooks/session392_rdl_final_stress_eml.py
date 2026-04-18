"""Session 392 notebook"""
import json, sys
sys.path.insert(0, "python")
from monogate.frontiers.rdl_final_stress_eml import analyze_rdl_final_stress_eml
result = analyze_rdl_final_stress_eml()
print(json.dumps(result, indent=2, default=str))
