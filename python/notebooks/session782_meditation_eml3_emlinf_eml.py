import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.meditation_eml3_emlinf_eml import analyze_meditation_eml3_emlinf_eml
result = analyze_meditation_eml3_emlinf_eml()
print(json.dumps(result, indent=2, default=str))
