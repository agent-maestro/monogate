import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.jury_deliberation_legal_eml import analyze_jury_deliberation_legal_eml
result = analyze_jury_deliberation_legal_eml()
print(json.dumps(result, indent=2, default=str))
