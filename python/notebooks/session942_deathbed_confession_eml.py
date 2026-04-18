import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.deathbed_confession_eml import analyze_deathbed_confession_eml
result = analyze_deathbed_confession_eml()
print(json.dumps(result, indent=2, default=str))