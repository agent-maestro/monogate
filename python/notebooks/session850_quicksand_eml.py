import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.quicksand_eml import analyze_quicksand_eml
result = analyze_quicksand_eml()
print(json.dumps(result, indent=2, default=str))