import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.hodge_adversarial4_eml import analyze_hodge_adversarial4_eml
result = analyze_hodge_adversarial4_eml()
print(json.dumps(result, indent=2))
