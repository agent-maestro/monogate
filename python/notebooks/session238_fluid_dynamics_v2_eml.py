import json, sys
sys.path.insert(0, 'D:/monogate/python')
from monogate.frontiers.fluid_dynamics_v2_eml import analyze_fluid_dynamics_v2_eml
result = analyze_fluid_dynamics_v2_eml()
print(json.dumps(result, indent=2, default=str))
