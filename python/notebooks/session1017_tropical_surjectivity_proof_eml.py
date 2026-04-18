import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.tropical_surjectivity_proof_eml import analyze_tropical_surjectivity_proof_eml
result = analyze_tropical_surjectivity_proof_eml()
print(json.dumps(result, indent=2))
