import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.campfire_mesmerize_eml import analyze_campfire_mesmerize_eml
result = analyze_campfire_mesmerize_eml()
print(json.dumps(result, indent=2, default=str))