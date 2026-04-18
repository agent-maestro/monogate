import json, sys
sys.path.insert(0, 'D:/monogate/python')
from monogate.frontiers.algebraic_geometry_v3_eml import analyze_algebraic_geometry_v3_eml
result = analyze_algebraic_geometry_v3_eml()
print(json.dumps(result, indent=2, default=str))
