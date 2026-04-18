import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.flat_joke_eml import analyze_flat_joke_eml
result = analyze_flat_joke_eml()
print(json.dumps(result, indent=2, default=str))