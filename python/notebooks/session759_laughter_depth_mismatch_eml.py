import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.laughter_depth_mismatch_eml import analyze_laughter_depth_mismatch_eml
result = analyze_laughter_depth_mismatch_eml()
print(json.dumps(result, indent=2, default=str))
