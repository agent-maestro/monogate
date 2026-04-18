import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.five_prize_paper_eml import analyze_five_prize_paper_eml
result = analyze_five_prize_paper_eml()
print(json.dumps(result, indent=2))
