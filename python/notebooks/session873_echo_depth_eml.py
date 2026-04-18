import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.echo_depth_eml import analyze_echo_depth_eml
result = analyze_echo_depth_eml()
print(json.dumps(result, indent=2, default=str))