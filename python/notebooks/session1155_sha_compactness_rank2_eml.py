import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.sha_compactness_rank2_eml import analyze_sha_compactness_rank2_eml
result = analyze_sha_compactness_rank2_eml()
print(json.dumps(result, indent=2))
