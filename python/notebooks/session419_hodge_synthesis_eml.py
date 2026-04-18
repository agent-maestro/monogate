import json, sys
sys.path.insert(0, 'python')
from monogate.frontiers.hodge_synthesis_eml import analyze_hodge_synthesis_eml
result = analyze_hodge_synthesis_eml()
print(json.dumps(result, indent=2, default=str))
