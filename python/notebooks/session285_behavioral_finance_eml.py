import json, sys
sys.path.insert(0, "python")
from monogate.frontiers.behavioral_finance_eml import analyze_behavioral_finance_eml
result = analyze_behavioral_finance_eml()
print(json.dumps(result, indent=2, default=str))
