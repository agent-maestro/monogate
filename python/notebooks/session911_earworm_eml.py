import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.earworm_eml import analyze_earworm_eml
result = analyze_earworm_eml()
print(json.dumps(result, indent=2, default=str))