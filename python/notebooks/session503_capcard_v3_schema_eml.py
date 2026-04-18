"""Session 503 notebook"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.capcard_v3_schema_eml import analyze_capcard_v3_schema_eml
print(json.dumps(analyze_capcard_v3_schema_eml(), indent=2, default=str))
