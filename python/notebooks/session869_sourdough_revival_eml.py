import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.sourdough_revival_eml import analyze_sourdough_revival_eml
result = analyze_sourdough_revival_eml()
print(json.dumps(result, indent=2, default=str))