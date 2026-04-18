import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.height_pairing_matrix_eml import analyze_height_pairing_matrix_eml
result = analyze_height_pairing_matrix_eml()
print(json.dumps(result, indent=2))
