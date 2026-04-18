import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.spectral_natural_proof_eml import analyze_spectral_natural_proof_eml
result = analyze_spectral_natural_proof_eml()
print(json.dumps(result, indent=2))
