import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.ym_dual_attack_eml import analyze_ym_dual_attack_eml
result = analyze_ym_dual_attack_eml()
print(json.dumps(result, indent=2, default=str))
