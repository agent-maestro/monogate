import json, sys
sys.path.insert(0, 'D:/monogate/python')
from monogate.frontiers.topos_higher_eml import analyze_topos_higher_eml
result = analyze_topos_higher_eml()
print(json.dumps(result, indent=2, default=str))
