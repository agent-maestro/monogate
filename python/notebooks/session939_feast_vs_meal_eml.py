import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.feast_vs_meal_eml import analyze_feast_vs_meal_eml
result = analyze_feast_vs_meal_eml()
print(json.dumps(result, indent=2, default=str))