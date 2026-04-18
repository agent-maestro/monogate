import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.apology_hierarchy_eml import analyze_apology_hierarchy_eml
result = analyze_apology_hierarchy_eml()
print(json.dumps(result, indent=2, default=str))
