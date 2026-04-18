import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.dialogue_conversation_depth_eml import analyze_dialogue_conversation_depth_eml
result = analyze_dialogue_conversation_depth_eml()
print(json.dumps(result, indent=2, default=str))
