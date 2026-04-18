import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.hodge_state_of_play_eml import analyze_hodge_state_of_play_eml
result = analyze_hodge_state_of_play_eml()
print(json.dumps(result, indent=2, default=str))