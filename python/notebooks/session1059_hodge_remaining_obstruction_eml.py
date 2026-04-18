import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.hodge_remaining_obstruction_eml import analyze_hodge_remaining_obstruction_eml
result = analyze_hodge_remaining_obstruction_eml()
print(json.dumps(result, indent=2))
