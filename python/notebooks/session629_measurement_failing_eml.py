import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.measurement_failing_eml import analyze_measurement_failing_eml
result = analyze_measurement_failing_eml()
print(json.dumps(result, indent=2, default=str))
