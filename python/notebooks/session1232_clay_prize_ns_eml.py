import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.clay_prize_ns_eml import analyze_clay_prize_ns_eml
result = analyze_clay_prize_ns_eml()
print(json.dumps(result, indent=2))
