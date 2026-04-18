import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.crying_at_weddings_eml import analyze_crying_at_weddings_eml
result = analyze_crying_at_weddings_eml()
print(json.dumps(result, indent=2, default=str))