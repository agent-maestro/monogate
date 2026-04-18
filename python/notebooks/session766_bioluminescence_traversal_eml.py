import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.bioluminescence_traversal_eml import analyze_bioluminescence_traversal_eml
result = analyze_bioluminescence_traversal_eml()
print(json.dumps(result, indent=2, default=str))
