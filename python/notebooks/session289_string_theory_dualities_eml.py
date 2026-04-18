import json, sys
sys.path.insert(0, "python")
from monogate.frontiers.string_theory_dualities_eml import analyze_string_theory_dualities_eml
result = analyze_string_theory_dualities_eml()
print(json.dumps(result, indent=2, default=str))
