"""Session 462 notebook"""
import json, sys
sys.path.insert(0, "D:/monogate/python")
from monogate.frontiers.full_dependency_audit_eml import analyze_full_dependency_audit_eml
print(json.dumps(analyze_full_dependency_audit_eml(), indent=2, default=str))
