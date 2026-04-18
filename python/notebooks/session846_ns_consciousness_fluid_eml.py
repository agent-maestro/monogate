import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.ns_consciousness_fluid_eml import analyze_ns_consciousness_fluid_eml
result = analyze_ns_consciousness_fluid_eml()
print(json.dumps(result, indent=2, default=str))