import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.ym_full_proof_assembly_eml import analyze_ym_full_proof_assembly_eml
result = analyze_ym_full_proof_assembly_eml()
print(json.dumps(result, indent=2))
