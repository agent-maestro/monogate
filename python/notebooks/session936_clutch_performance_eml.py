import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.clutch_performance_eml import analyze_clutch_performance_eml
result = analyze_clutch_performance_eml()
print(json.dumps(result, indent=2, default=str))