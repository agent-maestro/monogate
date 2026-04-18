import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.frequencies_oscillatory_eml import analyze_frequencies_oscillatory_eml
result = analyze_frequencies_oscillatory_eml()
print(json.dumps(result, indent=2, default=str))
