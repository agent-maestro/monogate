import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.hodge_derham_comparison_eml import analyze_hodge_derham_comparison_eml
result = analyze_hodge_derham_comparison_eml()
print(json.dumps(result, indent=2))
