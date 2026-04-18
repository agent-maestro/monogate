import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.paper_folding_eml import analyze_paper_folding_eml
result = analyze_paper_folding_eml()
print(json.dumps(result, indent=2, default=str))