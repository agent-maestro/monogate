import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.information_perplexity_eml import analyze_information_perplexity_eml
result = analyze_information_perplexity_eml()
print(json.dumps(result, indent=2, default=str))
