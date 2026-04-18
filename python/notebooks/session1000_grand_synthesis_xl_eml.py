import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.grand_synthesis_xl_eml import analyze_grand_synthesis_xl_eml
result = analyze_grand_synthesis_xl_eml()
print(json.dumps(result, indent=2, default=str))