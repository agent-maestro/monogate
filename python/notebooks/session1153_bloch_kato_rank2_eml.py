import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.bloch_kato_rank2_eml import analyze_bloch_kato_rank2_eml
result = analyze_bloch_kato_rank2_eml()
print(json.dumps(result, indent=2))
