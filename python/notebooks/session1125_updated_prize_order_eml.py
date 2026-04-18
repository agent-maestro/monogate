import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.updated_prize_order_eml import analyze_updated_prize_order_eml
result = analyze_updated_prize_order_eml()
print(json.dumps(result, indent=2))
