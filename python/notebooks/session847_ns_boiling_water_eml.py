import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.ns_boiling_water_eml import analyze_ns_boiling_water_eml
result = analyze_ns_boiling_water_eml()
print(json.dumps(result, indent=2, default=str))