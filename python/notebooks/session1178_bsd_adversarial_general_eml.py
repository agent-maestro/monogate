import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.bsd_adversarial_general_eml import analyze_bsd_adversarial_general_eml
result = analyze_bsd_adversarial_general_eml()
print(json.dumps(result, indent=2))
