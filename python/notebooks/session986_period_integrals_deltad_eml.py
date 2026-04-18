import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.period_integrals_deltad_eml import analyze_period_integrals_deltad_eml
result = analyze_period_integrals_deltad_eml()
print(json.dumps(result, indent=2, default=str))