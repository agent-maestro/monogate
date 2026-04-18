"""Session 465 notebook"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.shadow_normalization_final_eml import analyze_shadow_normalization_final_eml
print(json.dumps(analyze_shadow_normalization_final_eml(), indent=2, default=str))
