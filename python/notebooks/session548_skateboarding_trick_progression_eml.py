import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.skateboarding_trick_progression_eml import analyze_skateboarding_trick_progression_eml
result = analyze_skateboarding_trick_progression_eml()
print(json.dumps(result, indent=2, default=str))
