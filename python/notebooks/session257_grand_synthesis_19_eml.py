import json, sys
sys.path.insert(0, 'D:/monogate/python')
from monogate.frontiers.grand_synthesis_19_eml import analyze_grand_synthesis_19_eml
result = analyze_grand_synthesis_19_eml()
print(json.dumps(result, indent=2, default=str))
