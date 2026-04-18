"""Session 396 notebook"""
import json, sys
sys.path.insert(0, "python")
from monogate.frontiers.rdl_gl3_attack_eml import analyze_rdl_gl3_attack_eml
result = analyze_rdl_gl3_attack_eml()
print(json.dumps(result, indent=2, default=str))
