"""Session 189 — Category Theory Deep II: Yoneda Strata & Categorical Asymmetry (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.category_v3_eml import analyze_category_v3_eml
print(json.dumps(analyze_category_v3_eml(), indent=2, default=str))
