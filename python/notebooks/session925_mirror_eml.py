import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.mirror_eml import analyze_mirror_eml
result = analyze_mirror_eml()
print(json.dumps(result, indent=2, default=str))