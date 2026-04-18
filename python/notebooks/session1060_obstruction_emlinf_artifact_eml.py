import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.obstruction_emlinf_artifact_eml import analyze_obstruction_emlinf_artifact_eml
result = analyze_obstruction_emlinf_artifact_eml()
print(json.dumps(result, indent=2))
