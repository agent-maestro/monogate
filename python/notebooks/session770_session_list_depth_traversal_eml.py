import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.session_list_depth_traversal_eml import analyze_session_list_depth_traversal_eml
result = analyze_session_list_depth_traversal_eml()
print(json.dumps(result, indent=2, default=str))
