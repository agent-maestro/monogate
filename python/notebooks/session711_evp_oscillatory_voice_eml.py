import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.evp_oscillatory_voice_eml import analyze_evp_oscillatory_voice_eml
result = analyze_evp_oscillatory_voice_eml()
print(json.dumps(result, indent=2, default=str))
