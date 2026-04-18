import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.hodge_grand_synthesis_eml import analyze_hodge_grand_synthesis_eml
result = analyze_hodge_grand_synthesis_eml()
print(json.dumps(result, indent=2))
