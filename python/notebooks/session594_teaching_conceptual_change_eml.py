import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.teaching_conceptual_change_eml import analyze_teaching_conceptual_change_eml
result = analyze_teaching_conceptual_change_eml()
print(json.dumps(result, indent=2, default=str))
