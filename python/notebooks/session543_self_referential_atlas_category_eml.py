import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.self_referential_atlas_category_eml import analyze_self_referential_atlas_category_eml
result = analyze_self_referential_atlas_category_eml()
print(json.dumps(result, indent=2, default=str))
