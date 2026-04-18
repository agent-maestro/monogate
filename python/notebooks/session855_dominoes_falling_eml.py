import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.dominoes_falling_eml import analyze_dominoes_falling_eml
result = analyze_dominoes_falling_eml()
print(json.dumps(result, indent=2, default=str))