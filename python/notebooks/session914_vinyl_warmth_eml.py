import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.vinyl_warmth_eml import analyze_vinyl_warmth_eml
result = analyze_vinyl_warmth_eml()
print(json.dumps(result, indent=2, default=str))