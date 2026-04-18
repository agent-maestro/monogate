import json, sys
sys.path.insert(0, 'python')
from monogate.frontiers.hodge_lefschetz_eml import analyze_hodge_lefschetz_eml
result = analyze_hodge_lefschetz_eml()
print(json.dumps(result, indent=2, default=str))
