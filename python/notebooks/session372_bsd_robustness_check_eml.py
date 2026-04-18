import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.bsd_robustness_check_eml import analyze_bsd_robustness_check_eml
result = analyze_bsd_robustness_check_eml()
with open(f'python/results/session372_bsd_robustness_check_eml.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2, default=str)
print(f'Session 372 OK')
