import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.procrastination_eml import analyze_procrastination_eml
result = analyze_procrastination_eml()
print(json.dumps(result, indent=2, default=str))