import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.epigenetics_eml2_eml import analyze_epigenetics_eml2_eml
result = analyze_epigenetics_eml2_eml()
print(json.dumps(result, indent=2, default=str))
