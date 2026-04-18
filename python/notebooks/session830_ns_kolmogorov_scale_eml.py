import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.ns_kolmogorov_scale_eml import analyze_ns_kolmogorov_scale_eml
result = analyze_ns_kolmogorov_scale_eml()
print(json.dumps(result, indent=2, default=str))