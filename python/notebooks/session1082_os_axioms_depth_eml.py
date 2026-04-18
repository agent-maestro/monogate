import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.os_axioms_depth_eml import analyze_os_axioms_depth_eml
result = analyze_os_axioms_depth_eml()
print(json.dumps(result, indent=2))
