import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.thunder_lightning_eml import analyze_thunder_lightning_eml
result = analyze_thunder_lightning_eml()
print(json.dumps(result, indent=2, default=str))