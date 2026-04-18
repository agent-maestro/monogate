import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.yang_mills_hodge_eml import analyze_yang_mills_hodge_eml
result = analyze_yang_mills_hodge_eml()
print(json.dumps(result, indent=2))
