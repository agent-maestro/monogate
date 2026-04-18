import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.beehive_thermoregulation_eml import analyze_beehive_thermoregulation_eml
result = analyze_beehive_thermoregulation_eml()
print(json.dumps(result, indent=2, default=str))