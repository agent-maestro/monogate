import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.absences_cascading_downward_eml import analyze_absences_cascading_downward_eml
result = analyze_absences_cascading_downward_eml()
print(json.dumps(result, indent=2, default=str))
