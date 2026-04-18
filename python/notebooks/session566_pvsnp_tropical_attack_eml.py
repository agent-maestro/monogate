import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.pvsnp_tropical_attack_eml import analyze_pvsnp_tropical_attack_eml
result = analyze_pvsnp_tropical_attack_eml()
print(json.dumps(result, indent=2, default=str))
