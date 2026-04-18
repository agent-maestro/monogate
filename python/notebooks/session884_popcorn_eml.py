import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.popcorn_eml import analyze_popcorn_eml
result = analyze_popcorn_eml()
print(json.dumps(result, indent=2, default=str))