import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.ns_consciousness_t567_eml import analyze_ns_consciousness_t567_eml
result = analyze_ns_consciousness_t567_eml()
print(json.dumps(result, indent=2))
