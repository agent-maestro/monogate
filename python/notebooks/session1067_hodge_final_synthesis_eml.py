import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.hodge_final_synthesis_eml import analyze_hodge_final_synthesis_eml
result = analyze_hodge_final_synthesis_eml()
print(json.dumps(result, indent=2))
