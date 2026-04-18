import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.hodge_a5_analog_eml import analyze_hodge_a5_analog_eml
result = analyze_hodge_a5_analog_eml()
print(json.dumps(result, indent=2, default=str))