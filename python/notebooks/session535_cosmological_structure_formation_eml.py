import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.cosmological_structure_formation_eml import analyze_cosmological_structure_formation_eml
result = analyze_cosmological_structure_formation_eml()
print(json.dumps(result, indent=2, default=str))
