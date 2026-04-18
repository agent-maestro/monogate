import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.silence_conversation_pause_eml import analyze_silence_conversation_pause_eml
result = analyze_silence_conversation_pause_eml()
print(json.dumps(result, indent=2, default=str))
