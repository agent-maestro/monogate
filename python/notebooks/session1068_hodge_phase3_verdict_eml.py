import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.hodge_phase3_verdict_eml import analyze_hodge_phase3_verdict_eml
result = analyze_hodge_phase3_verdict_eml()
print(json.dumps(result, indent=2))
