import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.hodge_codim_induction_eml import analyze_hodge_codim_induction_eml
result = analyze_hodge_codim_induction_eml()
print(json.dumps(result, indent=2))
