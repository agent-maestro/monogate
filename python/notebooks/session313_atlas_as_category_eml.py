"""Session 313 — Atlas as Category"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.atlas_as_category_eml import analyze_atlas_as_category_eml
result = analyze_atlas_as_category_eml()
print(json.dumps(result, indent=2, default=str))
