import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.persuasion_rhetoric_eml import analyze_persuasion_rhetoric_eml
result = analyze_persuasion_rhetoric_eml()
print(json.dumps(result, indent=2, default=str))
