import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.pnp_provability_question_eml import analyze_pnp_provability_question_eml
result = analyze_pnp_provability_question_eml()
print(json.dumps(result, indent=2))
