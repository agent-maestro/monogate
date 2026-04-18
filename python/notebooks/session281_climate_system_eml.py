import json, sys
sys.path.insert(0, "python")
from monogate.frontiers.climate_system_eml import analyze_climate_system_eml
result = analyze_climate_system_eml()
print(json.dumps(result, indent=2, default=str))
