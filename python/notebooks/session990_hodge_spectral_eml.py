import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.hodge_spectral_eml import analyze_hodge_spectral_eml
result = analyze_hodge_spectral_eml()
print(json.dumps(result, indent=2, default=str))