import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.placebo_effect_eml import analyze_placebo_effect_eml
result = analyze_placebo_effect_eml()
print(json.dumps(result, indent=2, default=str))