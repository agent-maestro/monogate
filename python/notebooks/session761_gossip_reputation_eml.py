import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.gossip_reputation_eml import analyze_gossip_reputation_eml
result = analyze_gossip_reputation_eml()
print(json.dumps(result, indent=2, default=str))
