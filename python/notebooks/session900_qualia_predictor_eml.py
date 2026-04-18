import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.qualia_predictor_eml import analyze_qualia_predictor_eml
result = analyze_qualia_predictor_eml()
print(json.dumps(result, indent=2, default=str))