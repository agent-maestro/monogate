import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.vibrational_healing_eml import analyze_vibrational_healing_eml
result = analyze_vibrational_healing_eml()
print(json.dumps(result, indent=2, default=str))
