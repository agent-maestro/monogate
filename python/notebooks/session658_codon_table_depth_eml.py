import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.codon_table_depth_eml import analyze_codon_table_depth_eml
result = analyze_codon_table_depth_eml()
print(json.dumps(result, indent=2, default=str))
