import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.climate_tipping_cascades_eml import analyze_climate_tipping_cascades_eml
result = analyze_climate_tipping_cascades_eml()
print(json.dumps(result, indent=2, default=str))
