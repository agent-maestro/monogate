import sys, json
sys.path.insert(0, 'python')
from monogate.frontiers.bsd_tropical_semiring_eml import analyze_bsd_tropical_semiring_eml
result = analyze_bsd_tropical_semiring_eml()
with open(f'python/results/session362_bsd_tropical_semiring_eml.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2, default=str)
print(f'Session 362 OK')
