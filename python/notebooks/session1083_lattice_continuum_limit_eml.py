import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.lattice_continuum_limit_eml import analyze_lattice_continuum_limit_eml
result = analyze_lattice_continuum_limit_eml()
print(json.dumps(result, indent=2))
