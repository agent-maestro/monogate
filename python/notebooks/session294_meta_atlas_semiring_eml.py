import json, sys
sys.path.insert(0, "python")
from monogate.frontiers.meta_atlas_semiring_eml import analyze_meta_atlas_semiring_eml
result = analyze_meta_atlas_semiring_eml()
print(json.dumps(result, indent=2, default=str))
