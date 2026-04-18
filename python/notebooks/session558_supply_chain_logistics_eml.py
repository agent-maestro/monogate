import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.supply_chain_logistics_eml import analyze_supply_chain_logistics_eml
result = analyze_supply_chain_logistics_eml()
print(json.dumps(result, indent=2, default=str))
