import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.ym_4d_construction_gap_eml import analyze_ym_4d_construction_gap_eml
result = analyze_ym_4d_construction_gap_eml()
print(json.dumps(result, indent=2))
