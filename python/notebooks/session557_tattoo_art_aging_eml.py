import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.tattoo_art_aging_eml import analyze_tattoo_art_aging_eml
result = analyze_tattoo_art_aging_eml()
print(json.dumps(result, indent=2, default=str))
