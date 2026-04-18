"""Session 223 — eml4 primitive count eml (notebook script)"""
import json, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from monogate.frontiers.eml4_primitive_count_eml import analyze_eml4_primitive_count_eml
print(json.dumps(analyze_eml4_primitive_count_eml(), indent=2, default=str))
