import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.gct_eml_representation_eml import analyze_gct_eml_representation_eml
result = analyze_gct_eml_representation_eml()
print(json.dumps(result, indent=2))
