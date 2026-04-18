import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.bsd_rh_grand_unification_eml import analyze_bsd_rh_grand_unification_eml
result = analyze_bsd_rh_grand_unification_eml()
with open(f'python/results/session373_bsd_rh_grand_unification_eml.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2, default=str)
print(f'Session 373 OK')
