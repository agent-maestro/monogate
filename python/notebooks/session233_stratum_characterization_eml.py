import json, sys
sys.path.insert(0, 'D:/monogate/python')
from monogate.frontiers.stratum_characterization_eml import analyze_stratum_characterization_eml
result = analyze_stratum_characterization_eml()
print(json.dumps(result, indent=2, default=str))
