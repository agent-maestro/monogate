import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.absolute_hodge_eml import analyze_absolute_hodge_eml
result = analyze_absolute_hodge_eml()
print(json.dumps(result, indent=2, default=str))