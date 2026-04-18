import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.hodge_luc30_deep_eml import analyze_hodge_luc30_deep_eml
result = analyze_hodge_luc30_deep_eml()
print(json.dumps(result, indent=2, default=str))