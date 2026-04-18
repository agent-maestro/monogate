import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.psychedelic_experience_eml import analyze_psychedelic_experience_eml
result = analyze_psychedelic_experience_eml()
print(json.dumps(result, indent=2, default=str))
