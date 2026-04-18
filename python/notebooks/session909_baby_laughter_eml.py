import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.baby_laughter_eml import analyze_baby_laughter_eml
result = analyze_baby_laughter_eml()
print(json.dumps(result, indent=2, default=str))