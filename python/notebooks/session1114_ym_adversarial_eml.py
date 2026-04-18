import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.ym_adversarial_eml import analyze_ym_adversarial_eml
result = analyze_ym_adversarial_eml()
print(json.dumps(result, indent=2))
