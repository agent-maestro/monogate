import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.eml_qft_classification_eml import analyze_eml_qft_classification_eml
result = analyze_eml_qft_classification_eml()
print(json.dumps(result, indent=2))
