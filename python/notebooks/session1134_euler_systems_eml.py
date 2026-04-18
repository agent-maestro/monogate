import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.euler_systems_eml import analyze_euler_systems_eml
result = analyze_euler_systems_eml()
print(json.dumps(result, indent=2))
