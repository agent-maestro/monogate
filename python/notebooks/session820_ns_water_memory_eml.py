import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.ns_water_memory_eml import analyze_ns_water_memory_eml
result = analyze_ns_water_memory_eml()
print(json.dumps(result, indent=2, default=str))