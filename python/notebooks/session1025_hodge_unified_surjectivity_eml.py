import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.hodge_unified_surjectivity_eml import analyze_hodge_unified_surjectivity_eml
result = analyze_hodge_unified_surjectivity_eml()
print(json.dumps(result, indent=2))
