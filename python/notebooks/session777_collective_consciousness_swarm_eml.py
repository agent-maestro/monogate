import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.collective_consciousness_swarm_eml import analyze_collective_consciousness_swarm_eml
result = analyze_collective_consciousness_swarm_eml()
print(json.dumps(result, indent=2, default=str))
