import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.addiction_recovery_neuroscience_eml import analyze_addiction_recovery_neuroscience_eml
result = analyze_addiction_recovery_neuroscience_eml()
print(json.dumps(result, indent=2, default=str))
