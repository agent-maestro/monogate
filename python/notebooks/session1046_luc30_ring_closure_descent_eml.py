import sys, json
sys.path.insert(0, "python")
from monogate.frontiers.luc30_ring_closure_descent_eml import analyze_luc30_ring_closure_descent_eml
result = analyze_luc30_ring_closure_descent_eml()
print(json.dumps(result, indent=2))
