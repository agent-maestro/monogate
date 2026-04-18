import json, sys
sys.path.insert(0, 'D:/monogate/python')
from monogate.frontiers.algebraic_geometry_shadow_eml import analyze_algebraic_geometry_shadow_eml
print(json.dumps(analyze_algebraic_geometry_shadow_eml(), indent=2, default=str))
