import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.four_prize_paper_eml import analyze_four_prize_paper_eml
result = analyze_four_prize_paper_eml()
print(json.dumps(result, indent=2))
