import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.aqft_eml import analyze_aqft_eml
result = analyze_aqft_eml()
print(json.dumps(result, indent=2))
