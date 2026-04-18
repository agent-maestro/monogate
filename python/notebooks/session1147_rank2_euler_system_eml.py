import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.rank2_euler_system_eml import analyze_rank2_euler_system_eml
result = analyze_rank2_euler_system_eml()
print(json.dumps(result, indent=2))
