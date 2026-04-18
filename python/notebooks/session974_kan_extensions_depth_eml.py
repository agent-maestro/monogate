import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.kan_extensions_depth_eml import analyze_kan_extensions_depth_eml
result = analyze_kan_extensions_depth_eml()
print(json.dumps(result, indent=2, default=str))