import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.ym_lattice_shadow_eml import analyze_ym_lattice_shadow_eml
result = analyze_ym_lattice_shadow_eml()
print(json.dumps(result, indent=2, default=str))
