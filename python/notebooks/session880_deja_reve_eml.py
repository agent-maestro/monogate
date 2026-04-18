import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.deja_reve_eml import analyze_deja_reve_eml
result = analyze_deja_reve_eml()
print(json.dumps(result, indent=2, default=str))