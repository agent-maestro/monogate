import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.ns_regularity_type2_eml import analyze_ns_regularity_type2_eml
result = analyze_ns_regularity_type2_eml()
print(json.dumps(result, indent=2, default=str))
