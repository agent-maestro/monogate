import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.tropical_logic_theorem_proving_eml import analyze_tropical_logic_theorem_proving_eml
result = analyze_tropical_logic_theorem_proving_eml()
print(json.dumps(result, indent=2, default=str))
