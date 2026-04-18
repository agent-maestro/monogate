import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.return_to_eml0_atoms_eml import analyze_return_to_eml0_atoms_eml
result = analyze_return_to_eml0_atoms_eml()
print(json.dumps(result, indent=2, default=str))
