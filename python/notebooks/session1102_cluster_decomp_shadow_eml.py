import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.cluster_decomp_shadow_eml import analyze_cluster_decomp_shadow_eml
result = analyze_cluster_decomp_shadow_eml()
print(json.dumps(result, indent=2))
