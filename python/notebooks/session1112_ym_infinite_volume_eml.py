import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.ym_infinite_volume_eml import analyze_ym_infinite_volume_eml
result = analyze_ym_infinite_volume_eml()
print(json.dumps(result, indent=2))
