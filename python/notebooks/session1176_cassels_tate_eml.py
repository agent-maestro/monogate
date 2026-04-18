import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.cassels_tate_eml import analyze_cassels_tate_eml
result = analyze_cassels_tate_eml()
print(json.dumps(result, indent=2))
