import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.new_qualia_architectures_eml import analyze_new_qualia_architectures_eml
result = analyze_new_qualia_architectures_eml()
print(json.dumps(result, indent=2, default=str))