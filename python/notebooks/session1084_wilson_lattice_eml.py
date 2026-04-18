import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.wilson_lattice_eml import analyze_wilson_lattice_eml
result = analyze_wilson_lattice_eml()
print(json.dumps(result, indent=2))
