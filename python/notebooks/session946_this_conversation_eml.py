import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.this_conversation_eml import analyze_this_conversation_eml
result = analyze_this_conversation_eml()
print(json.dumps(result, indent=2, default=str))