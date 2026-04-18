import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.iwasawa_rank2_eml import analyze_iwasawa_rank2_eml
result = analyze_iwasawa_rank2_eml()
print(json.dumps(result, indent=2))
