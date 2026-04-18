import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.topological_qc_eml import analyze_topological_qc_eml
result = analyze_topological_qc_eml()
print(json.dumps(result, indent=2, default=str))