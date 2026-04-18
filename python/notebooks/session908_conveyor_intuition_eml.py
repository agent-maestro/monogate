import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.conveyor_intuition_eml import analyze_conveyor_intuition_eml
result = analyze_conveyor_intuition_eml()
print(json.dumps(result, indent=2, default=str))