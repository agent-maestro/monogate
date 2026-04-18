import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.first_bite_best_eml import analyze_first_bite_best_eml
result = analyze_first_bite_best_eml()
print(json.dumps(result, indent=2, default=str))