import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.predictive_model_tropical_eml import analyze_predictive_model_tropical_eml
result = analyze_predictive_model_tropical_eml()
print(json.dumps(result, indent=2, default=str))
