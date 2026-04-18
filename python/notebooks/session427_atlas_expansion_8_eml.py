import json, sys
sys.path.insert(0, 'python')
from monogate.frontiers.atlas_expansion_8_eml import analyze_atlas_expansion_8_eml
result = analyze_atlas_expansion_8_eml()
print(json.dumps(result, indent=2, default=str))
