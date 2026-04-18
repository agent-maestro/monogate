import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.bsd_regulator_coefficient_eml import analyze_bsd_regulator_coefficient_eml
result = analyze_bsd_regulator_coefficient_eml()
with open(f'python/results/session358_bsd_regulator_coefficient_eml.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2, default=str)
print(f'Session 358 OK')
