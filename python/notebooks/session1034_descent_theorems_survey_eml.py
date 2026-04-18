import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.descent_theorems_survey_eml import analyze_descent_theorems_survey_eml
result = analyze_descent_theorems_survey_eml()
print(json.dumps(result, indent=2))
