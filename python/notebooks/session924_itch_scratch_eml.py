import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.itch_scratch_eml import analyze_itch_scratch_eml
result = analyze_itch_scratch_eml()
print(json.dumps(result, indent=2, default=str))