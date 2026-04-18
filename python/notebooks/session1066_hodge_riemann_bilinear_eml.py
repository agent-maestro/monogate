import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.hodge_riemann_bilinear_eml import analyze_hodge_riemann_bilinear_eml
result = analyze_hodge_riemann_bilinear_eml()
print(json.dumps(result, indent=2))
