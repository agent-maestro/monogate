import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.consciousness_self_referential_fp_eml import analyze_consciousness_self_referential_fp_eml
result = analyze_consciousness_self_referential_fp_eml()
print(json.dumps(result, indent=2, default=str))
