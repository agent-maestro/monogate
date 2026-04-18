import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.weight_surjectivity_engine_eml import analyze_weight_surjectivity_engine_eml
result = analyze_weight_surjectivity_engine_eml()
print(json.dumps(result, indent=2))
