import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.frequency_altered_states_eml import analyze_frequency_altered_states_eml
result = analyze_frequency_altered_states_eml()
print(json.dumps(result, indent=2, default=str))
