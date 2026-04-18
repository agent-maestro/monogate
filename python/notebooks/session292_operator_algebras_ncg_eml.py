import json, sys
sys.path.insert(0, "python")
from monogate.frontiers.operator_algebras_ncg_eml import analyze_operator_algebras_ncg_eml
result = analyze_operator_algebras_ncg_eml()
print(json.dumps(result, indent=2, default=str))
