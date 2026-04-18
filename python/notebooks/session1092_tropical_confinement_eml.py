import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.tropical_confinement_eml import analyze_tropical_confinement_eml
result = analyze_tropical_confinement_eml()
print(json.dumps(result, indent=2))
