import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.handshake_trust_eml import analyze_handshake_trust_eml
result = analyze_handshake_trust_eml()
print(json.dumps(result, indent=2, default=str))
