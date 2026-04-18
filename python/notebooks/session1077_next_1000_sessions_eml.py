import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.next_1000_sessions_eml import analyze_next_1000_sessions_eml
result = analyze_next_1000_sessions_eml()
print(json.dumps(result, indent=2))
