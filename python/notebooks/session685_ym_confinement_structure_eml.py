import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.ym_confinement_structure_eml import analyze_ym_confinement_structure_eml
result = analyze_ym_confinement_structure_eml()
print(json.dumps(result, indent=2, default=str))
