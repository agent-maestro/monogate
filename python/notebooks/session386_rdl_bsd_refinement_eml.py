"""Session 386 notebook"""
import json, sys
sys.path.insert(0, "python")
from monogate.frontiers.rdl_bsd_refinement_eml import analyze_rdl_bsd_refinement_eml
result = analyze_rdl_bsd_refinement_eml()
print(json.dumps(result, indent=2, default=str))
