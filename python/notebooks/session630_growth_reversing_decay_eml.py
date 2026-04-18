import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.growth_reversing_decay_eml import analyze_growth_reversing_decay_eml
result = analyze_growth_reversing_decay_eml()
print(json.dumps(result, indent=2, default=str))
