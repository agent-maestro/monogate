import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.seed_germination_eml import analyze_seed_germination_eml
result = analyze_seed_germination_eml()
print(json.dumps(result, indent=2, default=str))