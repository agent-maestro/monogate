import json, sys
sys.path.insert(0, "python")
from monogate.frontiers.amorphous_materials_eml import analyze_amorphous_materials_eml
result = analyze_amorphous_materials_eml()
print(json.dumps(result, indent=2, default=str))
