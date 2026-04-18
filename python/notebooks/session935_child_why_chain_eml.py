import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.child_why_chain_eml import analyze_child_why_chain_eml
result = analyze_child_why_chain_eml()
print(json.dumps(result, indent=2, default=str))