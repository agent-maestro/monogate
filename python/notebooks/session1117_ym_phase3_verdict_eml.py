import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.ym_phase3_verdict_eml import analyze_ym_phase3_verdict_eml
result = analyze_ym_phase3_verdict_eml()
print(json.dumps(result, indent=2))
