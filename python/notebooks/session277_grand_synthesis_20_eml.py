import json, sys
sys.path.insert(0, 'D:/monogate/python')
from monogate.frontiers.grand_synthesis_20_eml import analyze_grand_synthesis_20_eml
print(json.dumps(analyze_grand_synthesis_20_eml(), indent=2, default=str))
