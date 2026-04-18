import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.prison_recidivism_eml import analyze_prison_recidivism_eml
result = analyze_prison_recidivism_eml()
print(json.dumps(result, indent=2, default=str))
