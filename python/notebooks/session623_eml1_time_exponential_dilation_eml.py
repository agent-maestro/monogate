import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.eml1_time_exponential_dilation_eml import analyze_eml1_time_exponential_dilation_eml
result = analyze_eml1_time_exponential_dilation_eml()
print(json.dumps(result, indent=2, default=str))
