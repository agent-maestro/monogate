import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.sha_categorification_eml import analyze_sha_categorification_eml
result = analyze_sha_categorification_eml()
print(json.dumps(result, indent=2))
