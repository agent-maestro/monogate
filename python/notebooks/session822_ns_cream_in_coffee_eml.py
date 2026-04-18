import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.ns_cream_in_coffee_eml import analyze_ns_cream_in_coffee_eml
result = analyze_ns_cream_in_coffee_eml()
print(json.dumps(result, indent=2, default=str))