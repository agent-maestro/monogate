import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.attention_depth_transitions_eml import analyze_attention_depth_transitions_eml
result = analyze_attention_depth_transitions_eml()
print(json.dumps(result, indent=2, default=str))
