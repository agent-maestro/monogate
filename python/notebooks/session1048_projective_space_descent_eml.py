import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.projective_space_descent_eml import analyze_projective_space_descent_eml
result = analyze_projective_space_descent_eml()
print(json.dumps(result, indent=2))
