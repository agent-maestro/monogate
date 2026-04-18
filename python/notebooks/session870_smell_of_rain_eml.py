import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.smell_of_rain_eml import analyze_smell_of_rain_eml
result = analyze_smell_of_rain_eml()
print(json.dumps(result, indent=2, default=str))