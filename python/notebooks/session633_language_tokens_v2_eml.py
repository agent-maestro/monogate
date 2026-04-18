import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.language_tokens_v2_eml import analyze_language_tokens_v2_eml
result = analyze_language_tokens_v2_eml()
print(json.dumps(result, indent=2, default=str))
