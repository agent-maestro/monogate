import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.market_opening_bell_eml import analyze_market_opening_bell_eml
result = analyze_market_opening_bell_eml()
print(json.dumps(result, indent=2, default=str))