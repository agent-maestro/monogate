import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.eml2_time_logarithmic_compression_eml import analyze_eml2_time_logarithmic_compression_eml
result = analyze_eml2_time_logarithmic_compression_eml()
print(json.dumps(result, indent=2, default=str))
