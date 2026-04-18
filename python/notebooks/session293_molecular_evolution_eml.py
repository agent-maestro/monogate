import json, sys
sys.path.insert(0, "python")
from monogate.frontiers.molecular_evolution_eml import analyze_molecular_evolution_eml
result = analyze_molecular_evolution_eml()
print(json.dumps(result, indent=2, default=str))
