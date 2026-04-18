import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.hodge_adversarial_review_eml import analyze_hodge_adversarial_review_eml
result = analyze_hodge_adversarial_review_eml()
print(json.dumps(result, indent=2, default=str))