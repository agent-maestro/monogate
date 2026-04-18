import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.duy_transfer_eml import analyze_duy_transfer_eml
result = analyze_duy_transfer_eml()
print(json.dumps(result, indent=2))
