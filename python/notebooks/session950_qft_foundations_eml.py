import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.qft_foundations_eml import analyze_qft_foundations_eml
result = analyze_qft_foundations_eml()
print(json.dumps(result, indent=2, default=str))