import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.motivic_cohomology_eml import analyze_motivic_cohomology_eml
result = analyze_motivic_cohomology_eml()
print(json.dumps(result, indent=2, default=str))