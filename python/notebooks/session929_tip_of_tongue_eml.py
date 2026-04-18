import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.tip_of_tongue_eml import analyze_tip_of_tongue_eml
result = analyze_tip_of_tongue_eml()
print(json.dumps(result, indent=2, default=str))