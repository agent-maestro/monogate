import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.eml4_mass_gap_eml import analyze_eml4_mass_gap_eml
result = analyze_eml4_mass_gap_eml()
print(json.dumps(result, indent=2))
