import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.millennium_scorecard_eml import analyze_millennium_scorecard_eml
result = analyze_millennium_scorecard_eml()
print(json.dumps(result, indent=2))
