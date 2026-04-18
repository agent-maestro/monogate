import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.millennium_langlands_eml import analyze_millennium_langlands_eml
result = analyze_millennium_langlands_eml()
print(json.dumps(result, indent=2, default=str))
