import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.invisible_forces_gravity_eml import analyze_invisible_forces_gravity_eml
result = analyze_invisible_forces_gravity_eml()
print(json.dumps(result, indent=2, default=str))
